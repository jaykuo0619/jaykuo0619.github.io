# 2026 縣市長選舉：專業版預估（貝氏民調整合＋機構偏差＋歷史誤差＋全國連動蒙地卡羅）
# 輸入：../data.json（model.py 產生，含全部民調與方法查核）
# 輸出：forecast_pro.json 與文字摘要
import json, math, random, datetime as dt, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
D=json.load(open(os.path.join(HERE,'..','data.json')))
TODAY=dt.date.fromisoformat(D['today']); EDAY=dt.date.fromisoformat(D['eday'])
MULTI={'花蓮縣','彰化縣'}           # 三強以上，分享率模擬
NOSWING={'金門縣','連江縣','花蓮縣'} # 無民進黨主要候選人，不套藍綠全國擺盪

def dd(s): return dt.date.fromisoformat(s)

# ---------- 參數（可做敏感度） ----------
BASE=dict(
  kappa=0.6,        # 時間漂移：每天增加的差距變異（點²）；依台北 6～11 月約 25 點的實際移動校準
  tau=3.0,          # 民調非抽樣誤差（點，差距單位）
  ai_sd=9.0,        # AI 模擬的總誤差（點）
  web_extra=4.0,    # 網路非機率樣本額外誤差（點）
  party_extra=3.0,  # 政黨／競辦委託額外誤差（點）
  deff=1.6,         # 設計效應
  n_default=800,    # 樣本數未公布時
  he_prior=4.0,     # 機構偏差先驗標準差（點）
  prior_sd=9.0,     # 基準（2022＋全國擺盪＋候選人）先驗標準差
  county_err=4.5,   # 選舉日縣市獨立誤差（點，t 分配 df=5）
  nat_err=3.0,      # 全國共同誤差（藍綠同向，點）
  und_k=0.25,       # 未表態分配不確定：SD = und_k × 未表態% 
  window=200,       # 只用最近幾天的民調（5 月以後；舊民調靠時間漂移自然降權）
  nat_mean=0.0,     # 全國共同誤差的平均（情境分析用；正＝綠營比民調好）
  use_he=True, min_tr=0, phone_only=False, no_sp=False, since=None, no_ai=False,
)

def camp_of(c): return c['camp']  # G 綠、B 藍營（含藍白共推）、X 其他

def two_way(race):
    cs=race['cands']
    g=[c for c in cs if c['camp']=='G']; b=[c for c in cs if c['camp']=='B']; x=[c for c in cs if c['camp']=='X' and c['n']!='其他']
    if g and b: return max(g,key=lambda c:c['prior'])['n'], max(b,key=lambda c:c['prior'])['n']
    # 無綠營：藍營 vs 最大其他
    o=sorted([c for c in cs if c['n']!='其他'],key=lambda c:-c['prior'])
    return o[1]['n'], o[0]['n']   # 「A」=挑戰者、「B」=領先者（符號：A−B）

def poll_sd(p,P):
    n=p['n'] if p['n'] and not p['est'] else P['n_default']
    samp=2*math.sqrt(P['deff']*0.25/n)*100     # 差距的抽樣標準差
    var=samp**2+P['tau']**2
    if p['t']=='ai': var=P['ai_sd']**2
    if p['t']=='online': var+=P['web_extra']**2
    if p['sp'] or 'adv' in (p['fl'] or []): var+=P['party_extra']**2
    q=max(0.25,p['q']); var/=q                  # 方法／透明度分數低→變異放大
    return math.sqrt(var)

def margin(p,A,B):
    a=p['v'].get(A); b=p['v'].get(B)
    if a is None or b is None or a+b<=0: return None
    return (a-b)/(a+b)*100

def usable(p,P):
    if p['t']=='party': return False
    age=(TODAY-dd(p['fe'])).days
    if age>P['window']: return False
    if P['since'] and dd(p['fe'])<dd(P['since']): return False
    if P['min_tr'] and p['tr']<P['min_tr']: return False
    if P['phone_only'] and p['t']!='phone': return False
    if P['no_sp'] and (p['sp'] or 'adv' in (p['fl'] or [])): return False
    if P['no_ai'] and p['t']=='ai': return False
    return True

def is_proj(p): return '封關' in p['org'] and '戴立安' in p['org']

# ---------- 機構偏差：跨縣市聯合估計（ridge／隨機效果） ----------
def house_effects(P):
    obs=[]
    for c,r in D['races'].items():
        if c in MULTI or c in NOSWING: continue
        A,B=two_way(r)
        for p in r['polls']:
            if not usable(p,P) or is_proj(p): continue
            m=margin(p,A,B)
            if m is None: continue
            age=(TODAY-dd(p['fe'])).days
            sd=poll_sd(p,P); w=1/(sd**2)
            obs.append(dict(c=c,h=p['house'],m=m,fe=dd(p['fe']),w=w,t=p['t']))
    he={}
    for it in range(30):
        # 各縣市局部趨勢（其他機構、±30 天、時間核），扣掉目前機構偏差
        res={}
        for o in obs:
            ref=[(q['m']-he.get(q['h'],0), q['w']*math.exp(-abs((q['fe']-o['fe']).days)/20)) for q in obs if q['c']==o['c'] and q['h']!=o['h'] and abs((q['fe']-o['fe']).days)<=30]
            if not ref: continue
            mu=sum(m*w for m,w in ref)/sum(w for m,w in ref)
            res.setdefault(o['h'],[]).append((o['m']-mu,o['w']))
        new={}
        for h,v in res.items():
            # 貝氏收縮：先驗 N(0, he_prior²)；每筆觀測的有效變異約 1/w×2（含參考值誤差）
            prec=sum(w/2 for d,w in v)+1/P['he_prior']**2
            new[h]=sum(d*w/2 for d,w in v)/prec
        # 以樣本加權置中（偏差是相對於整個民調業平均）
        if new:
            mean=sum(new.values())/len(new)
            new={h:x-mean for h,x in new.items()}
        if all(abs(new.get(h,0)-he.get(h,0))<0.01 for h in set(new)|set(he)): he=new; break
        he=new
    return he

def county_poll_avg(c,r,P,he):
    A,B=two_way(r); xs=[]
    for p in r['polls']:
        if not usable(p,P): continue
        m=margin(p,A,B)
        if m is None: continue
        if P['use_he'] and not is_proj(p) and c not in MULTI and c not in NOSWING: m-=he.get(p['house'],0)
        age=(TODAY-dd(p['fe'])).days
        sd=poll_sd(p,P); var=sd**2+P['kappa']*age
        xs.append((m,var,p))
    if not xs: return None
    # 同一機構多份：只算有效獨立資訊（同機構權重合計上限 = 最新一份的 1.5 倍）
    byh={}
    for m,v,p in xs: byh.setdefault(p['house'],[]).append((m,v,p))
    num=den=0.0
    for h,arr in byh.items():
        ws=[1/v for m,v,p in arr]; cap=1.5*max(ws)
        scale=min(1.0,cap/sum(ws))
        for (m,v,p),w in zip(arr,ws): num+=m*w*scale; den+=w*scale
    mu=num/den; var=1/den
    unds=[p['und'] for m,v,p in xs if p.get('und') is not None]
    und=sum(unds)/len(unds) if unds else 20.0
    return dict(mu=mu,var=var,n=len(xs),und=und,polls=xs)

def prior_margin(r):
    A,B=two_way(r); pr={c['n']:c['prior'] for c in r['cands']}
    return (pr[A]-pr[B])/(pr[A]+pr[B])*100

def multi_shares(c,r,P):
    names=[x['n'] for x in r['cands'] if x['n']!='其他']
    pr={x['n']:x['prior'] for x in r['cands'] if x['n']!='其他'}
    acc={n:0.0 for n in names}; W=0.0; unds=[]
    for p in r['polls']:
        if not usable(p,P): continue
        named=[n for n in names if n in p['v']]
        if len(named)<2: continue
        tot=sum(p['v'][n] for n in named); prn=sum(pr[n] for n in named)
        age=(TODAY-dd(p['fe'])).days
        w=1/(poll_sd(p,P)**2+P['kappa']*age)
        for n in names: acc[n]+=w*((p['v'][n]/tot*prn) if n in named else pr[n])
        W+=w
        if p.get('und') is not None: unds.append(p['und'])
    tp=sum(pr.values())
    prior={n:pr[n]/tp*100 for n in names}
    if W==0: return prior, None, 20.0
    pa={n:acc[n]/W for n in names}; s=sum(pa.values()); pa={n:pa[n]/s*100 for n in names}
    # 貝氏合併（份額空間，先驗 SD = prior_sd/2，民調 SD = 1/sqrt(W)/2）
    vp=(1/W)/4; v0=(P['prior_sd']/2)**2
    post={n:(pa[n]/vp+prior[n]/v0)/(1/vp+1/v0) for n in names}
    s=sum(post.values()); post={n:post[n]/s*100 for n in names}
    return post, math.sqrt(1/(1/vp+1/v0)), (sum(unds)/len(unds) if unds else 20.0)

def run(P=None, sims=40000, seed=7, detail=True):
    P=dict(BASE,**(P or {})); rnd=random.Random(seed)
    he=house_effects(P) if P['use_he'] else {}
    out={}
    for c,r in D['races'].items():
        pmap={x['n']:x['p'] for x in r['cands']}
        if c in MULTI:
            post,psd,und=multi_shares(c,r,P)
            out[c]=dict(kind='multi',post=post,psd=psd,und=und,pmap=pmap,n=sum(1 for p in r['polls'] if usable(p,P)))
            continue
        A,B=two_way(r); m0=prior_margin(r); avg=county_poll_avg(c,r,P,he)
        if avg:
            v0=P['prior_sd']**2; post=(avg['mu']/avg['var']+m0/v0)/(1/avg['var']+1/v0); pv=1/(1/avg['var']+1/v0); und=avg['und']; npoll=avg['n']; pm=avg['mu']
        else:
            post=m0; pv=(P['prior_sd']+1.5)**2; und=25.0; npoll=0; pm=None
        sign=1 if pmap[A]=='D' else 0   # A 是綠營時，全國擺盪正值有利 A
        out[c]=dict(kind='two',A=A,B=B,prior=m0,pollavg=pm,post=post,psd=math.sqrt(pv),und=und,n=npoll,sign=sign,pmap=pmap)
    # ---------- 蒙地卡羅 ----------
    wins={c:{} for c in out}; seatdist={}; marg={c:[] for c in out}
    def t5(): # 標準化 t(5)
        z=rnd.gauss(0,1); ch=sum(rnd.gauss(0,1)**2 for _ in range(5))
        return z/math.sqrt(ch/5)/math.sqrt(5/3)
    for s in range(sims):
        nat=rnd.gauss(P['nat_mean'],P['nat_err'])   # 正值＝綠營全面比民調好
        seats={'K':0,'D':0,'T':0,'I':0}
        for c,o in out.items():
            if o['kind']=='two':
                e=o['psd']*rnd.gauss(0,1)+P['county_err']*t5()+P['und_k']*o['und']*rnd.gauss(0,1)
                if c not in NOSWING: e+= nat if o['sign'] else -nat
                m=o['post']+e; w=o['A'] if m>0 else o['B']
                marg[c].append(m)
            else:
                sh={}
                for n,v in o['post'].items():
                    e=(o['psd'] or P['prior_sd']/2)*rnd.gauss(0,1)+P['county_err']*t5()+P['und_k']/1.5*o['und']*rnd.gauss(0,1)
                    if c not in NOSWING:
                        if o['pmap'][n]=='D': e+=nat/2
                        elif o['pmap'][n]=='K': e-=nat/2
                    sh[n]=max(0.5,v+e)
                w=max(sh,key=sh.get)
            wins[c][w]=wins[c].get(w,0)+1
            seats[o['pmap'][w]]+=1
        k=(seats['K'],seats['D'],seats['T'],seats['I'])
        seatdist[k]=seatdist.get(k,0)+1
    res={}
    for c,o in out.items():
        wp={n:v/sims for n,v in wins[c].items()}
        d=dict(kind=o['kind'],wp=wp,n=o['n'],und=round(o['und'],1))
        if o['kind']=='two':
            ms=sorted(marg[c]); lo,hi=ms[int(.1*sims)],ms[int(.9*sims)]
            # 二人得票率（扣掉其他候選人預估占比）
            oth=100-sum(x['prior'] for x in D['races'][c]['cands'] if x['n'] in (o['A'],o['B']))
            oth=max(0,min(15,oth))
            sa=(100-oth)*(0.5+o['post']/200); sb=(100-oth)-sa
            d.update(A=o['A'],B=o['B'],prior=round(o['prior'],1),pollavg=None if o['pollavg'] is None else round(o['pollavg'],1),post=round(o['post'],1),lo=round(lo,1),hi=round(hi,1),shareA=round(sa,1),shareB=round(sb,1))
        else:
            d.update(post={n:round(v,1) for n,v in o['post'].items()})
        res[c]=d
    K=[k[0] for k,v in seatdist.items() for _ in range(v)]; Dd=[k[1] for k,v in seatdist.items() for _ in range(v)]
    K.sort(); Dd.sort()
    seats=dict(K_mean=round(sum(K)/sims,2),D_mean=round(sum(Dd)/sims,2),K_80=(K[int(.1*sims)],K[int(.9*sims)]),D_80=(Dd[int(.1*sims)],Dd[int(.9*sims)]),
               top=sorted(((v/sims,k) for k,v in seatdist.items()),reverse=True)[:6],
               pK_more=sum(v for k,v in seatdist.items() if k[0]>k[1])/sims, pD_more=sum(v for k,v in seatdist.items() if k[1]>k[0])/sims, ptie=sum(v for k,v in seatdist.items() if k[0]==k[1])/sims)
    return dict(params=P,he={h:round(x,2) for h,x in sorted(he.items(),key=lambda kv:kv[1])},races=res,seats=seats)

if __name__=='__main__':
    main=run()
    variants={
      '主模型':{},
      '不校正機構偏差':dict(use_he=False),
      '只用高透明（tr≥75）電訪':dict(min_tr=75,phone_only=True),
      '排除政黨／競辦委託':dict(no_sp=True),
      '只用 10/20 後民調':dict(since='2026-10-20'),
      '排除 AI 模擬':dict(no_ai=True),
      '全國誤差加大到 5 點':dict(nat_err=5.0),
      '情境：民調整體低估藍營 3 點':dict(nat_mean=-3.0),
      '情境：民調整體低估綠營 3 點':dict(nat_mean=3.0),
    }
    sens={}
    for name,v in variants.items():
        r=main if not v else run(v,sims=20000)
        sens[name]=dict(seats=r['seats'],wp={c:x['wp'] for c,x in r['races'].items()})
    json.dump(dict(main=main,sens=sens),open(os.path.join(HERE,'forecast_pro.json'),'w'),ensure_ascii=False,indent=1,default=str)
    print('機構偏差（正＝偏綠）:',main['he'])
    for c,x in main['races'].items():
        if x['kind']=='two':
            lead=max(x['wp'],key=x['wp'].get)
            print(f"{c} {x['A']}−{x['B']} 先驗{x['prior']:+} 民調{x['pollavg']} 後驗{x['post']:+} 80%[{x['lo']},{x['hi']}] 勝率 {lead} {x['wp'][lead]:.1%} n={x['n']} und={x['und']}")
        else:
            print(c,x['post'],{k:f"{v:.1%}" for k,v in x['wp'].items()},'n=',x['n'])
    print('席次',main['seats'])
    for name,s in sens.items():
        print(name, 'K',s['seats']['K_mean'],'D',s['seats']['D_mean'], {c:f"{max(w.values()):.0%}{max(w,key=w.get)}" for c,w in s['wp'].items() if c in ('台北市','新北市','台中市','基隆市','新竹縣','嘉義市','宜蘭縣','雲林縣','台東縣','花蓮縣','彰化縣')})
