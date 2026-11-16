# 把專業版模型（forecast_pro.json）的今日預估寫回 data.json，網站顯示的「今天」數字改由專業版決定
# 歷史走勢（6/1 起每日）仍是原模型逐日重算，今天這一天改成專業版結果
import json, os
H=os.path.dirname(os.path.abspath(__file__))
DP=os.path.join(H,'..','data.json')
D=json.load(open(DP)); F=json.load(open(os.path.join(H,'forecast_pro.json')))['main']
VALID_RATIO=0.985
def og(sh,party):
    g=[v for n,v in sh.items() if party.get(n)=='D']; o=[v for n,v in sh.items() if n!='其他' and party.get(n)!='D']
    return None if not g or not o else round(max(o)-max(g),2)
for c,r in D['races'].items():
    pr=F['races'][c]; last=r['series'][-1]; party={x['n']:x['p'] for x in r['cands']}
    old=dict(last['s'])
    if pr['kind']=='two':
        A,B=pr['A'],pr['B']
        oth={n:v for n,v in old.items() if n not in (A,B)}
        R=100-sum(oth.values())
        sh=dict(oth); sh[A]=R*(0.5+pr['post']/200); sh[B]=R-sh[A]
        lohi={A:(R*(0.5+pr['lo']/200),R*(0.5+pr['hi']/200))}; lohi[B]=(R-lohi[A][1],R-lohi[A][0])
    else:
        oth={n:v for n,v in old.items() if n not in pr['post']}
        R=100-sum(oth.values()); tot=sum(pr['post'].values())
        sh=dict(oth); sh.update({n:v/tot*R for n,v in pr['post'].items()})
        lohi={n:(sh[n]-(r['proj'][n]['pct']-r['proj'][n]['lo']),sh[n]+(r['proj'][n]['hi']-r['proj'][n]['pct'])) for n in pr['post']}
    order=sorted(sh,key=lambda n:-sh[n]); lead,sec=order[0],order[1]
    wp=pr['wp'].get(lead,0.0)
    # 專業版的勝者若與得票率領先者不同（極少數），以勝率最高者為準
    wl=max(pr['wp'],key=pr['wp'].get)
    if wl!=lead: lead=wl; sec=order[0] if order[0]!=wl else order[1]; wp=pr['wp'][wl]
    last.update(s={n:round(v,2) for n,v in sh.items()}, lead=lead, m=round(sh[lead]-sh[sec],2), wp=round(wp,4), og=og(sh,party), pro=True)
    t=r['turnout']; to=round(t['base']+(2.0 if wp<0.65 else 1.0 if wp<0.85 else 0.0),2)
    valid=t['electorate']*to/100*VALID_RATIO; t.update(t=to,valid=int(round(valid,-2)))
    for n in r['proj']:
        p=r['proj'][n]; p['pct']=round(sh[n],2); p['votes']=int(round(valid*sh[n]/100,-2))
        if n in lohi: p['lo']=round(max(0,lohi[n][0]),1); p['hi']=round(min(100,lohi[n][1]),1)
    r['pro']=dict(A=pr.get('A'),B=pr.get('B'),und=pr.get('und'),wp=pr['wp'],post=pr.get('post'),lo=pr.get('lo'),hi=pr.get('hi'),prior=pr.get('prior'),pollavg=pr.get('pollavg'),n=pr['n'])
# 全國今日
nat=D['national'][-1]; seats={'K':0,'D':0,'T':0,'I':0}; exp={k:0.0 for k in seats}; vb=vg=vt=0.0
for c,r in D['races'].items():
    party={x['n']:x['p'] for x in r['cands']}; camp={x['n']:x['camp'] for x in r['cands']}
    last=r['series'][-1]; seats[party[last['lead']]]+=1
    for n,w in F['races'][c]['wp'].items(): exp[party[n]]+=w
    v=r['turnout']['valid']
    for n,s in last['s'].items():
        if camp[n]=='B': vb+=v*s/100
        elif camp[n]=='G': vg+=v*s/100
    vt+=v
nat.update(seats=seats,exp={k:round(x,2) for k,x in exp.items()},vb=round(vb/vt*100,2),vg=round(vg/vt*100,2),pro=True)
D['method']['pro']=dict(seats=F['seats'],he=F['he'],params={k:v for k,v in F['params'].items() if not isinstance(v,(list,dict))},
  note='今日預估採專業版：跨縣市機構偏差、隨機漫步時間衰減、貝氏先驗、縣市獨立誤差＋全國藍綠連動誤差，蒙地卡羅 4 萬次。')
json.dump(D,open(DP,'w'),ensure_ascii=False)
print('seats',seats,'exp',nat['exp'])
