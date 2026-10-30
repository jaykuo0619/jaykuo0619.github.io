# 台灣 2026 縣市長選舉預測模型：民調加權 + AI 結構基準 + 每日聲量滾動調整
import json, math, random, datetime as dt
D = dt.date
START, EDAY = D(2026,6,1), D(2026,11,28)
TODAY = min(dt.datetime.now(dt.timezone(dt.timedelta(hours=8))).date(), EDAY)  # 台北時間

# 候選人：(姓名, 政黨代碼)  K=國民黨 D=民進黨 T=民眾黨 I=無黨籍/其他
# prior：AI 結構基準（有效票占比 %），依 2022 結果、政黨基本盤、現任優勢、評論者評等綜合判斷；民調另行加權，不重複計入
R = {
 '台北市': dict(c=[('蔣萬安','K',56),('沈伯洋','D',42),('其他','I',2)], note='現任蔣萬安尋求連任；10 月多份民調顯示差距快速收斂，部分民調沈伯洋反超。'),
 '新北市': dict(c=[('李四川','K',50),('蘇巧慧','D',49),('其他','I',1)], note='侯友宜卸任，開放席次；藍綠民調互有領先，最膠著的直轄市。'),
 '桃園市': dict(c=[('張善政','K',60),('黃世杰','D',40)], note='現任張善政尋求連任，藍營基本盤穩固。'),
 '台中市': dict(c=[('江啓臣','K',57),('何欣純','D',42),('洪麗華','I',1)], note='盧秀燕卸任；江啓臣仍領先，但差距較年初縮小。'),
 '台南市': dict(c=[('陳亭妃','D',62),('謝龍介','K',37),('其他','I',1)], note='綠營傳統票倉，黃偉哲卸任。'),
 '高雄市': dict(c=[('賴瑞隆','D',55),('柯志恩','K',44),('其他','I',1)], note='陳其邁卸任；8 月網路民調一度五五波，負面新聞影響綠營聲量。'),
 '基隆市': dict(c=[('謝國樑','K',54),('童子瑋','D',44),('魏造文','I',2)], note='現任謝國樑尋求連任，童子瑋為市議會議長。'),
 '新竹市': dict(c=[('高虹安','I',61),('莊競程','D',34),('何志勇','I',5)], note='現任高虹安（無黨籍，原民眾黨）尋求連任，藍營未提名。'),
 '新竹縣': dict(c=[('徐欣瑩','K',52),('鄭朝方','D',45),('朱定瑀','I',3)], note='藍營長期執政，9 月民調鄭朝方領先，選情翻轉跡象。'),
 '苗栗縣': dict(c=[('鍾東錦','K',64),('陳品安','D',36)], note='現任鍾東錦（已回歸國民黨）尋求連任。'),
 '彰化縣': dict(c=[('陳素月','D',50),('魏平政','K',36),('邱建富','I',13),('陳重嘉','I',1)], note='王惠美卸任；藍營分裂（邱建富獨立參選），綠營領先。'),
 '南投縣': dict(c=[('許淑華','K',62),('溫世政','D',38)], note='現任許淑華尋求連任。'),
 '雲林縣': dict(c=[('張嘉郡','K',56),('劉建國','D',42),('其他','I',2)], note='張麗善卸任；劉建國再戰。'),
 '嘉義縣': dict(c=[('蔡易餘','D',60),('吳品叡','I',40)], note='翁章梁卸任；藍營禮讓無黨籍吳品叡組在野聯盟。'),
 '嘉義市': dict(c=[('王美惠','D',52),('張啓楷','T',45),('其他','I',3)], note='黃敏惠卸任；藍白合推民眾黨張啓楷。'),
 '屏東縣': dict(c=[('周春米','D',56),('蘇清泉','K',44)], note='現任周春米尋求連任，2022 年對手再度對決。'),
 '宜蘭縣': dict(c=[('林國漳','D',51),('吳宗憲','K',47),('其他','I',2)], note='林姿妙卸任；藍白合推吳宗憲，可能政黨輪替。'),
 '台東縣': dict(c=[('吳秀華','K',58),('陳瑩','D',40),('其他','I',2)], note='饒慶鈴卸任；10/20 起吳秀華家族涉農路弊案，聲量轉負。'),
 '花蓮縣': dict(c=[('游淑貞','K',44),('魏嘉賢','I',32),('張峻','I',21),('羅佩秦','I',3)], note='徐榛蔚卸任；國民黨提名游淑貞，反傅陣營張峻、魏嘉賢分別參選。'),
 '澎湖縣': dict(c=[('陳振中','K',47),('吳淑瑾','D',44),('其他','I',9)], note='陳光復受傷無法參選，妻吳淑瑾代夫出征。'),
 '金門縣': dict(c=[('陳玉珍','K',62),('李文良','I',14),('洪和成','I',12),('其他','I',12)], note='現任陳福海（2022 年以無黨籍當選）未登記參選；藍營立委陳玉珍參選。'),
 '連江縣': dict(c=[('王忠銘','K',58),('曹爾元','I',42)], note='王忠銘尋求連任。'),
}

# 民調：類型 phone=電訪 online=網路 ai=AI 模擬；sponsor 標示政黨相關委託
# fe=調查結束日（未載明者以發布日前推估，est=True）, rel=發布日
P = [
 dict(r='台北市', org='信民兩岸研究協會（戴立安）／畢肯', fe=D(2026,9,18), rel=D(2026,9,22), n=1076, t='phone', v={'蔣萬安':41.7,'沈伯洋':40.5}, url='https://www.mirrormedia.mg/external/setn_1911133'),
 dict(r='台北市', org='TVBS 民調中心', fe=D(2026,10,7), rel=D(2026,10,9), n=1120, t='phone', v={'蔣萬安':49,'沈伯洋':41}, url='https://udn.com/news/story/124652/9803622'),
 dict(r='台北市', org='信民兩岸研究協會（戴立安）', fe=D(2026,10,17), rel=D(2026,10,20), n=None, t='phone', est=True, v={'沈伯洋':50.3,'蔣萬安':33.3}, url='https://news.ltn.com.tw/topic/戴立安民調'),
 dict(r='台北市', org='聯合報系民意調查中心', fe=D(2026,10,25), rel=D(2026,10,28), n=1115, t='phone', v={'沈伯洋':45,'蔣萬安':41}, url='https://udn.com/news/story/124652/9840910'),
 dict(r='台北市', org='ETtoday 民調雲', fe=D(2026,10,25), rel=D(2026,10,27), n=1462, t='online', v={'蔣萬安':48.6,'沈伯洋':41.1}, url='https://www.ettoday.net/news/20261027/3261830.htm'),
 dict(r='台北市', org='山水民意（震傳媒委託）', fe=D(2026,10,19), rel=D(2026,10,22), n=1074, t='phone', v={'沈伯洋':42.8,'蔣萬安':39.0}, url='https://tw.news.yahoo.com/%E5%8F%B0%E5%8C%97%E7%9C%9F%E9%80%86%E9%A2%A8%E4%BA%86-%E6%B2%88%E4%BC%AF%E6%B4%8B%E6%9C%80%E6%96%B0%E6%B0%91%E8%AA%BF%E5%86%8D%E8%B6%85%E8%BB%8A%E8%94%A3%E8%90%AC%E5%AE%89-025949927.html'),
 dict(r='新北市', org='年代民調中心', fe=D(2026,8,26), rel=D(2026,8,28), n=1070, t='phone', v={'蘇巧慧':37.8,'李四川':32.2}, url='https://www.nownews.com/news/6870016'),
 dict(r='新北市', org='TVBS 民調中心（國民黨新北議會黨團公布）', fe=D(2026,10,3), rel=D(2026,10,7), n=1210, t='phone', sp='K', v={'李四川':42.6,'蘇巧慧':35.9}, url='https://www.nownews.com/news/6881356'),
 dict(r='新北市', org='信民兩岸研究協會（戴立安）', fe=D(2026,10,10), rel=D(2026,10,13), n=None, t='phone', est=True, v={'蘇巧慧':43.1,'李四川':30.0}, url='https://cna.com.tw/news/aipl/202610130087.aspx'),
 dict(r='桃園市', org='TPOC 台灣議題研究中心（AI 矽基樣本模擬）', fe=D(2026,10,26), rel=D(2026,10,28), n=13789, t='ai', v={'張善政':47.2,'黃世杰':34.3}, url='https://ctinews.com/news/items/89xp2VNXWe'),
 dict(r='桃園市', org='TPOC 台灣議題研究中心（AI 矽基樣本模擬）', fe=D(2026,9,29), rel=D(2026,9,29), n=13789, t='ai', v={'張善政':47.3,'黃世杰':36.5}, url='https://www.mirrormedia.mg/external/mnews_20260930nm005'),
 dict(r='台中市', org='TVBS 民調中心（國民黨台中議會黨團公布）', fe=D(2026,9,12), rel=D(2026,9,14), n=None, t='phone', sp='K', est=True, v={'江啓臣':45.1,'何欣純':32.5}, url='https://www.nownews.com/news/6874941'),
 dict(r='台中市', org='年代民調中心', fe=D(2026,10,4), rel=D(2026,10,6), n=1068, t='phone', v={'江啓臣':37.3,'何欣純':31.3,'洪麗華':1.1}, url='https://www.nownews.com/news/6881349'),
 dict(r='台南市', org='新台灣國策智庫（凱達格蘭基金會出資）', fe=D(2026,10,15), rel=D(2026,10,21), n=1071, t='phone', sp='D', v={'陳亭妃':59.4,'謝龍介':22.6,'其他':1.0}, url='https://news.ltn.com.tw/news/politics/breakingnews/5613318'),
 dict(r='高雄市', org='ETtoday 民調雲（網路問卷）', fe=D(2026,10,25), rel=D(2026,10,30), n=1338, t='online', v={'賴瑞隆':43.2,'柯志恩':43.1}, url='https://www.ettoday.net/news/20261030/3262904.htm'),
 dict(r='高雄市', org='ETtoday 民調雲（網路問卷）', fe=D(2026,8,30), rel=D(2026,9,11), n=1283, t='online', v={'柯志恩':43.8,'賴瑞隆':43.5}, url='https://www.storm.mg/article/11163759'),
 dict(r='高雄市', org='TPOC 台灣議題研究中心（AI 矽基樣本模擬）', fe=D(2026,10,19), rel=D(2026,10,20), n=20299, t='ai', v={'賴瑞隆':45.2,'柯志恩':35.2}, url='https://www.storm.mg/article/11174498'),
 dict(r='基隆市', org='山水民意（上報委託）', fe=D(2026,8,24), rel=D(2026,8,31), n=1068, t='phone', v={'謝國樑':38.6,'童子瑋':33.2}, url='https://www.nownews.com/news/6870740'),
 dict(r='基隆市', org='趨勢民調（國民黨基隆市黨部委託）', fe=D(2026,10,9), rel=D(2026,10,14), n=1070, t='phone', sp='K', v={'謝國樑':42.9,'童子瑋':38.3}, url='https://www.worldjournal.com/wj/story/121218/9816052'),
 dict(r='新竹縣', org='關鍵調查（台灣公共政策學會等記者會公布）', fe=D(2026,10,26), rel=D(2026,10,29), n=1070, t='phone', v={'徐欣瑩':44.1,'鄭朝方':37.7}, url='https://cnews.com.tw/224261029a03/'),
 dict(r='新竹縣', org='皮爾森數據（鄭朝方競辦公布）', fe=D(2026,10,18), rel=D(2026,10,27), n=3054, t='online', sp='D', v={'鄭朝方':50.3,'徐欣瑩':34.87,'朱定瑀':1.14}, url='https://www.storm.mg/article/11176074'),
 dict(r='新竹縣', org='皮爾森數據（鄭朝方競辦公布）', fe=D(2026,9,21), rel=D(2026,10,27), n=3098, t='online', sp='D', v={'鄭朝方':47.68,'徐欣瑩':33.34}, url='https://newtalk.tw/news/view/2026-10-27/1067646'),
 dict(r='新竹縣', org='年代民調中心', fe=D(2026,9,18), rel=D(2026,9,21), n=1069, t='phone', v={'鄭朝方':35.1,'徐欣瑩':28.7,'朱定瑀':2.8}, url='https://www.nownews.com/news/6877030'),
 dict(r='彰化縣', org='聯合報系民意調查中心', fe=D(2026,10,15), rel=D(2026,10,19), n=1003, t='phone', v={'陳素月':32,'魏平政':16,'邱建富':10,'陳重嘉':0.5}, url='https://www.worldjournal.com/wj/story/121218/9823489'),
 # ---- 5 月至 8 月（6/1 起的歷史會用到；5 月公布者在 6/1 視為當時最新民調）----
 dict(r='台北市', org='TVBS 民調中心', fe=D(2026,5,25), rel=D(2026,5,27), n=None, t='phone', est=True, v={'蔣萬安':58,'沈伯洋':30}, url='https://www.worldjournal.com/wj/story/121218/9530591'),
 dict(r='台北市', org='震傳媒', fe=D(2026,6,21), rel=D(2026,6,24), n=None, t='phone', est=True, v={'蔣萬安':55.2,'沈伯洋':27.5}, url='https://udn.com/news/story/124652/9586002'),
 dict(r='新北市', org='TVBS 民調中心（國民黨新北議會黨團委託）', fe=D(2026,6,6), rel=D(2026,6,8), n=1073, t='phone', sp='K', v={'李四川':39.2,'蘇巧慧':33.0}, url='https://www.ettoday.net/news/20260608/3179520.htm'),
 dict(r='台中市', org='匯流新聞網民調中心', fe=D(2026,5,12), rel=D(2026,5,14), n=1070, t='phone', v={'江啓臣':40.6,'何欣純':24.4}, url='https://www.nownews.com/news/6836161'),
 dict(r='高雄市', org='山水民意（上報委託）', fe=D(2026,4,29), rel=D(2026,5,6), n=2027, t='phone', v={'賴瑞隆':47,'柯志恩':30.7}, url='https://news.tvbs.com.tw/politics/3196526'),
 dict(r='高雄市', org='新台灣國策智庫（凱達格蘭基金會出資）', fe=D(2026,6,10), rel=D(2026,6,12), n=1094, t='phone', sp='D', v={'賴瑞隆':46.2,'柯志恩':28.4}, url='https://www.storm.mg/lifestyle/11140883'),
 dict(r='高雄市', org='鉅聞天下（方法未載明）', fe=D(2026,8,8), rel=D(2026,8,10), n=None, t='online', est=True, v={'賴瑞隆':47.78,'柯志恩':46.14}, url='https://udn.com/news/story/124652/9681827'),
 dict(r='新竹市', org='匯流新聞網民調中心', fe=D(2026,5,20), rel=D(2026,5,27), n=1068, t='phone', v={'高虹安':54.5,'莊競程':21.3}, url='https://www.storm.mg/article/11136232'),
 dict(r='新竹縣', org='年代民調中心', fe=D(2026,6,16), rel=D(2026,6,17), n=1068, t='phone', v={'徐欣瑩':32.3,'鄭朝方':30.5}, url='https://www.ettoday.net/news/20260617/3185150.htm'),
 dict(r='嘉義市', org='TVBS 民調中心', fe=D(2026,5,3), rel=D(2026,5,5), n=None, t='phone', est=True, v={'王美惠':43,'張啓楷':37}, url='https://www.storm.mg/keyword/張啓楷'),
 dict(r='嘉義市', org='關鍵調查（中天新聞報導）', fe=D(2026,7,12), rel=D(2026,7,20), n=1069, t='phone', v={'王美惠':41.5,'張啓楷':38.0}, url='https://tw.news.yahoo.com/2026%E5%98%89%E7%BE%A9%E5%B8%82%E9%95%B7%E9%81%B8%E6%88%B0%E6%9C%80%E6%96%B0%E6%B0%91%E8%AA%BF%E5%87%BA%E7%88%90-%E5%BC%B5%E5%95%93%E6%A5%B7%E7%B7%8A%E5%92%AC%E7%8E%8B%E7%BE%8E%E6%83%A0-100407302.html'),
 dict(r='宜蘭縣', org='藍白合整合民調（機構未載明）', fe=D(2026,5,2), rel=D(2026,5,4), n=None, t='phone', sp='K', est=True, v={'林國漳':28.9,'吳宗憲':27.6}, url='https://news.tvbs.com.tw/politics/3194681'),
 dict(r='台東縣', org='匯流新聞網民調中心（兩人對決題）', fe=D(2026,5,28), rel=D(2026,6,1), n=905, t='phone', v={'吳秀華':51.3,'陳瑩':22.4}, url='https://n.yam.com/Article/20260601432941'),
 dict(r='花蓮縣', org='風傳媒民調中心', fe=D(2026,7,23), rel=D(2026,7,29), n=1068, t='phone', v={'游淑貞':30.1,'魏嘉賢':22.1,'張峻':12.5}, url='https://www.storm.mg/article/11152459'),
 # ---- 10/27 戴立安 10 月國政民調（全國 1075 人，分區「想讓哪個政黨在你的縣市執政」；n 為依選舉人數推估的分區樣本）----
 dict(r='台北市', org='戴立安台灣民心調查（畢肯執行，台北＋新北分區）', fe=D(2026,10,22), rel=D(2026,10,27), n=112, t='party', v={'蔣萬安': 31.8, '沈伯洋': 47.1}, url='https://newtalk.tw/news/view/2026-10-27/1067619'),
 dict(r='新北市', org='戴立安台灣民心調查（畢肯執行，台北＋新北分區）', fe=D(2026,10,22), rel=D(2026,10,27), n=183, t='party', v={'李四川': 31.8, '蘇巧慧': 47.1}, url='https://newtalk.tw/news/view/2026-10-27/1067619'),
 dict(r='桃園市', org='戴立安台灣民心調查（畢肯執行，桃園分區）', fe=D(2026,10,22), rel=D(2026,10,27), n=101, t='party', v={'張善政': 41.6, '黃世杰': 27.7}, url='https://newtalk.tw/news/view/2026-10-27/1067619'),
 dict(r='台中市', org='戴立安台灣民心調查（畢肯執行，台中分區）', fe=D(2026,10,22), rel=D(2026,10,27), n=125, t='party', v={'江啓臣': 24.2, '何欣純': 43.9}, url='https://newtalk.tw/news/view/2026-10-27/1067619'),
 dict(r='台南市', org='戴立安台灣民心調查（畢肯執行，台南＋高雄分區）', fe=D(2026,10,22), rel=D(2026,10,27), n=85, t='party', v={'謝龍介': 20.3, '陳亭妃': 58.5}, url='https://newtalk.tw/news/view/2026-10-27/1067619'),
 dict(r='高雄市', org='戴立安台灣民心調查（畢肯執行，台南＋高雄分區）', fe=D(2026,10,22), rel=D(2026,10,27), n=126, t='party', v={'柯志恩': 20.3, '賴瑞隆': 58.5}, url='https://newtalk.tw/news/view/2026-10-27/1067619'),
 # ---- 10/23 新增 ----
 dict(r='基隆市', org='雨晴指標行銷（謝國樑競辦公布）', fe=D(2026,10,18), rel=D(2026,10,24), n=1070, t='phone', sp='K', v={'謝國樑':40.5,'童子瑋':33.2}, url='https://news.nextapple.com/politics/20261024/4D800FD179999C6AD822CF03435163E7'),
 dict(r='花蓮縣', org='風傳媒民調中心', fe=D(2026,10,18), rel=D(2026,10,25), n=1068, t='phone', v={'游淑貞':29.6,'張峻':17.8,'魏嘉賢':13.8}, url='https://tw.news.yahoo.com/%E8%8A%B1%E8%93%AE%E6%9C%80%E6%96%B0%E6%B0%91%E8%AA%BF-%E6%B8%B8%E6%B7%91%E8%B2%9E29-6-%E5%B1%85%E9%A6%96-3%E8%87%B310%E6%9C%88%E5%85%AD%E9%80%A3%E5%86%A0-065300349.html'),
 dict(r='基隆市', org='大地民意（鏡新聞委託）', fe=D(2026,10,21), rel=D(2026,10,23), n=1075, t='phone', v={'童子瑋':37.0,'謝國樑':36.3,'魏造文':0.8}, url='https://setn.com/news/1927095'),
 dict(r='台中市', org='世新大學民調中心（國民黨台中議會黨團委託）', fe=D(2026,10,16), rel=D(2026,10,17), n=1070, t='phone', sp='K', v={'江啓臣':39.8,'何欣純':28.7,'洪麗華':1.0}, url='https://www.ettoday.net/news/20261024/3260334.htm'),
]

# ---- 2022 年縣市長選舉結果（維基百科 2022 Taiwanese local elections，前兩名）----
# e=選舉人數, t=投票率, w/r=(姓名, 政黨, 得票率%)；政黨依當年實際所屬
PREV = {
 '新北市':dict(e=3316517,t=56.60,w=('侯友宜','K',62.42),r=('林佳龍','D',37.58)),
 '台北市':dict(e=2026769,t=67.70,w=('蔣萬安','K',42.29),r=('陳時中','D',31.93)),
 '桃園市':dict(e=1825127,t=59.46,w=('張善政','K',52.02),r=('鄭運鵬','D',40.03)),
 '台中市':dict(e=2274107,t=60.01,w=('盧秀燕','K',59.35),r=('蔡其昌','D',38.93)),
 '台南市':dict(e=1548203,t=58.68,w=('黃偉哲','D',48.80),r=('謝龍介','K',43.63)),
 '高雄市':dict(e=2282623,t=58.61,w=('陳其邁','D',58.10),r=('柯志恩','K',40.16)),
 '宜蘭縣':dict(e=374779,t=64.28,w=('林姿妙','K',50.76),r=('江聰淵','D',41.13)),
 '新竹縣':dict(e=452720,t=58.98,w=('楊文科','K',63.36),r=('周江杰','D',32.40)),
 '苗栗縣':dict(e=443908,t=67.20,w=('鍾東錦','I',42.66),r=('徐定禎','D',31.24)),
 '彰化縣':dict(e=1028606,t=64.90,w=('王惠美','K',56.75),r=('黃秀芳','D',41.94)),
 '南投縣':dict(e=406195,t=69.08,w=('許淑華','K',55.99),r=('蔡培慧','D',42.83)),
 '雲林縣':dict(e=559273,t=67.35,w=('張麗善','K',56.57),r=('劉建國','D',41.60)),
 '嘉義縣':dict(e=422568,t=67.32,w=('翁章梁','D',62.85),r=('王育敏','K',37.15)),
 '屏東縣':dict(e=679330,t=67.18,w=('周春米','D',49.09),r=('蘇清泉','K',46.59)),
 '台東縣':dict(e=177853,t=64.79,w=('饒慶鈴','K',61.22),r=('劉櫂豪','D',36.65)),
 '花蓮縣':dict(e=266058,t=57.56,w=('徐榛蔚','K',64.73),r=('Kolas Yotaka','D',32.04)),
 '澎湖縣':dict(e=90360,t=58.51,w=('陳光復','D',36.64),r=('賴峰偉','K',33.33)),
 '基隆市':dict(e=307913,t=60.16,w=('謝國樑','K',52.92),r=('蔡適應','D',39.01)),
 '新竹市':dict(e=350758,t=62.94,w=('高虹安','T',45.02),r=('沈慧虹','D',35.68)),
 '嘉義市':dict(e=213000,t=44.04,w=('黃敏惠','K',63.82),r=('李俊俋','D',34.95), note='2022 年因候選人過世延至 12/18 投票，投票率偏低；選舉人數為約略值'),
 '金門縣':dict(e=122294,t=39.32,w=('陳福海','I',49.34),r=('楊鎮浯','K',41.05)),
 '連江縣':dict(e=11810,t=72.99,w=('王忠銘','K',50.99),r=('曹爾元','I',42.12)),
}
PREV_NATIONAL = {'K':50.03,'D':41.62}  # 2022 全國縣市長總得票率（中選會統計，約略）
BLUE_ALLIED = {'張啓楷','吳品叡'}  # 藍營共推或禮讓的非國民黨候選人，計入藍營得票

def camp(name, party):
    if name=='其他': return 'X'
    if party=='D': return 'G'
    if party=='K' or name in BLUE_ALLIED: return 'B'
    return 'O'

def margin_og(shares, parties):
    """在野（非民進黨）最高者減民進黨最高者；沒有民進黨候選人時回傳 None"""
    g=[v for n,v in shares.items() if parties.get(n)=='D']
    o=[v for n,v in shares.items() if n!='其他' and parties.get(n)!='D']
    if not g or not o: return None
    return round(max(o)-max(g),2)

# 2026 投票率估計：以 2022 為基準，嘉義市改用正常年份水準；選情越接近，動員越強
def turnout_est(county, wp):
    base = 62.0 if county=='嘉義市' else PREV[county]['t']
    bump = 2.0 if wp<0.65 else 1.0 if wp<0.85 else 0.0
    return round(base+bump,2)
ELECTORATE_GROWTH = 1.005   # 選舉人數年增約略估計
VALID_RATIO = 0.985          # 有效票比例

TYPE_W = {'phone':1.0,'online':0.6,'ai':0.35,'party':0.4}  # party＝全國民調的分區「想讓哪黨執政」題，不是候選人對決題

# 9 月以前民調／資料，只用於設定 AI 基準（不進入每日民調平均）
BASE_REF = {
 '台北市':['壹蘋新聞網 8/4–8/6 網路投票（自選樣本，未納入）：蔣萬安 51.7%、沈伯洋 46.7%'],
 '新北市':['ETtoday 民調雲 3/21–22：李四川 43.3%、蘇巧慧 41.8%','TPOC 選情預測網 9/7：李四川 50.58%、蘇巧慧 49.42%'],
 '台南市':['皮爾森數據 2 月（網路）：陳亭妃 45.96%、謝龍介 40.57%'],
 '台中市':['TVBS 2025 年 1 月：江啓臣 50%、何欣純 26%'],
 '基隆市':['TVBS 3 月：謝國樑領先約 15 個百分點'],
 '宜蘭縣':['TVBS 3 月三腳督：林國漳 33%、吳宗憲 28%、陳琬惠 8%'],
 '花蓮縣':['TPOC/街頭民調 7 月：游淑貞 43%、魏嘉賢 33%、張峻 24%（非科學抽樣）'],
}

# 聲量事件（依新聞報導整理的時間點；強度為模型估計值）
# (縣市, 日期, 候選人, 強度 -1~+1, 說明)
# 輿情事件：新聞（醜聞、司法、重量級輔選、失言等）與民調公布（帶動話題與西瓜效應）都納入。
# 民調數字本身另外算進民調平均；這裡的「民調公布」只算公布後的聲量與話題效應。
# 格式：(縣市, 日期, 受影響候選人, 強度 -1~+1, 說明, 來源網址, 類型 news/poll)
EV = [
 ('桃園市', D(2026,10,28),'張善政', 0.2,'TPOC AI 模擬民調張善政領先 12.9 點、13 區全勝','https://ctinews.com/news/items/89xp2VNXWe','poll'),
 ('台北市', D(2026,10,28),'沈伯洋', 0.5,'聯合報民調沈伯洋 45% 領先蔣萬安 41%，藍營媒體民調也出現翻轉','https://udn.com/news/story/124652/9840910','poll'),
 ('台北市', D(2026,10,27),'蔣萬安', 0.4,'ETtoday 網路民調蔣萬安 48.6% 領先沈伯洋 7.5 點','https://www.ettoday.net/news/20261027/3261830.htm','poll'),
 ('台北市', D(2026,10,27),'沈伯洋', 0.3,'戴立安國政民調：沈伯洋好感度 47.8%，領先蔣萬安 10.9 點，蔣兩個月跌 10.9 點','https://www.storm.mg/article/11175935','poll'),
 ('基隆市', D(2026,10,24),'謝國樑', 0.3,'謝國樑競辦公布民調領先 7.3 點，反擊鏡新聞民調','https://news.nextapple.com/politics/20261024/4D800FD179999C6AD822CF03435163E7','poll'),
 ('花蓮縣', D(2026,10,25),'游淑貞', 0.2,'風傳媒民調游淑貞 29.6% 連續居首','https://tw.news.yahoo.com/%E8%8A%B1%E8%93%AE%E6%9C%80%E6%96%B0%E6%B0%91%E8%AA%BF-%E6%B8%B8%E6%B7%91%E8%B2%9E29-6-%E5%B1%85%E9%A6%96-3%E8%87%B310%E6%9C%88%E5%85%AD%E9%80%A3%E5%86%A0-065300349.html','poll'),
 ('花蓮縣', D(2026,10,25),'張峻', 0.3,'風傳媒民調張峻 17.8% 超車魏嘉賢','https://tw.news.yahoo.com/%E8%8A%B1%E8%93%AE%E6%9C%80%E6%96%B0%E6%B0%91%E8%AA%BF-%E6%B8%B8%E6%B7%91%E8%B2%9E29-6-%E5%B1%85%E9%A6%96-3%E8%87%B310%E6%9C%88%E5%85%AD%E9%80%A3%E5%86%A0-065300349.html','poll'),
 ('台北市', D(2026,10,18),'蔣萬安', 0.4,'台中市長盧秀燕出任蔣萬安競總主委，藍營稱用以穩住基本盤','https://www.worldjournal.com/wj/story/121218/9823490','news'),
 ('台北市', D(2026,10,21),'蔣萬安', -0.6,'《面對面》專訪「問 A 答 B」遭批','','news'),
 ('新北市', D(2026,10,13),'李四川', -0.3,'藍營質疑不利民調為認知作戰，引發爭論','','news'),
 ('台中市', D(2026,8,1),'江啓臣', 0.3,'現任市長盧秀燕出任江啓臣競總主委','https://www.nownews.com/news/6862116','news'),
 ('台南市', D(2026,10,21),'謝龍介', -0.4,'謝龍介批民調「侮辱選民」，爭議延燒','','news'),
 ('高雄市', D(2026,9,5),'賴瑞隆', -0.5,'綠營負面新聞延燒，評論者下修評等','','news'),
 ('嘉義縣', D(2026,9,19),'蔡易餘', 0.4,'蔡英文前總統輔選','','news'),
 ('嘉義縣', D(2026,9,27),'蔡易餘', 0.4,'賴清德總統輔選','','news'),
 ('嘉義縣', D(2026,10,6),'吳品叡', 0.3,'在野大聯盟競總成立','','news'),
 ('嘉義市', D(2026,10,19),'王美惠', -0.3,'幕後影響力爭議','','news'),
 ('嘉義市', D(2026,10,20),'張啓楷', -0.2,'張啓楷提告王美惠等人，選戰轉趨負面','','news'),
 ('台東縣', D(2026,9,20),'陳瑩', 0.5,'賴清德總統赴台東輔選','','news'),
 ('台東縣', D(2026,10,20),'吳秀華', -1.0,'前縣長吳俊立（吳秀華家族）涉農路弊案遭約談、聲押','','news'),
 ('台東縣', D(2026,10,21),'吳秀華', -0.6,'吳俊立交保境管，檢方抗告','','news'),
 ('花蓮縣', D(2026,9,10),'游淑貞', -0.3,'縣府救災表現受批評，延燒至接班人','','news'),
 ('花蓮縣', D(2026,10,13),'張峻', 0.7,'宣布童子賢出任競總主委','','news'),
 ('高雄市', D(2026,10,30),'柯志恩', 0.4,'ETtoday 網路民調賴瑞隆 43.2% 對柯志恩 43.1%，差距僅 0.1 點','https://www.ettoday.net/news/20261030/3262904.htm','poll'),
 ('新竹縣', D(2026,10,29),'徐欣瑩', 0.4,'關鍵調查市話民調徐欣瑩 44.1% 領先鄭朝方 37.7%','https://udn.com/news/story/124652/9845183','poll'),
 ('新竹縣', D(2026,10,27),'鄭朝方', 0.3,'鄭朝方競辦公布皮爾森網路民調領先 15.4 點','','poll'),
 ('新竹縣', D(2026,10,24),'徐欣瑩', 0.3,'竹檢搜索爭議引發「反司法介選」，評論指泛藍加速歸隊','','news'),
 ('台北市', D(2026,9,22),'沈伯洋', 0.5,'信民民調差距縮至 1.2 個百分點','','poll'),
 ('台北市', D(2026,10,9),'蔣萬安', 0.4,'TVBS 民調蔣萬安領先 8 個百分點','','poll'),
 ('台北市', D(2026,10,20),'沈伯洋', 0.9,'信民民調沈伯洋反超 17 個百分點，網路熱議','','poll'),
 ('台北市', D(2026,10,22),'沈伯洋', 0.4,'震傳媒民調沈伯洋領先 3.8 個百分點','','poll'),
 ('新北市', D(2026,10,7),'李四川', 0.5,'TVBS 民調李四川領先 6.7 個百分點','','poll'),
 ('新北市', D(2026,10,13),'蘇巧慧', 0.7,'信民民調蘇巧慧領先 13.1 個百分點','','poll'),
 ('台中市', D(2026,9,14),'江啓臣', 0.3,'TVBS 民調江啓臣領先 12.6 個百分點','','poll'),
 ('台南市', D(2026,10,21),'陳亭妃', 0.5,'民調大幅領先','','poll'),
 ('高雄市', D(2026,9,11),'柯志恩', 0.5,'ETtoday 民調柯志恩小幅領先','','poll'),
 ('高雄市', D(2026,10,20),'賴瑞隆', 0.3,'TPOC 模擬賴瑞隆領先 10 個百分點','','poll'),
 ('基隆市', D(2026,10,14),'謝國樑', 0.3,'藍營委託民調謝國樑領先 4.6 個百分點','','poll'),
 ('新竹縣', D(2026,9,21),'鄭朝方', 0.6,'年代民調鄭朝方領先 6.4 個百分點','','poll'),
 ('彰化縣', D(2026,10,19),'陳素月', 0.4,'聯合報民調陳素月領先','','poll'),
 ('台北市', D(2026,6,24),'蔣萬安', 0.4,'震傳媒民調蔣萬安領先近 28 個百分點','','poll'),
 ('新北市', D(2026,6,8),'李四川', 0.4,'藍營公布民調李四川領先 6.2 個百分點','','poll'),
 ('新北市', D(2026,8,28),'蘇巧慧', 0.5,'年代民調蘇巧慧領先 5.6 個百分點','','poll'),
 ('高雄市', D(2026,6,12),'賴瑞隆', 0.4,'民調賴瑞隆領先近 18 個百分點','','poll'),
 ('高雄市', D(2026,8,10),'柯志恩', 0.5,'鉅聞天下民調雙方差距縮至 1.6 個百分點','','poll'),
 ('新竹縣', D(2026,6,17),'徐欣瑩', 0.3,'年代民調徐欣瑩小幅領先','','poll'),
 ('嘉義市', D(2026,7,20),'張啓楷', 0.4,'民調張啓楷差距縮至 3.5 個百分點','','poll'),
 ('台東縣', D(2026,6,1),'吳秀華', 0.4,'匯流民調吳秀華大幅領先','','poll'),
 ('花蓮縣', D(2026,7,29),'游淑貞', 0.3,'風傳媒民調游淑貞居首','','poll'),
 ('基隆市', D(2026,8,31),'童子瑋', 0.4,'上報民調：確定投票者雙方幾乎平手','','poll'),
 ('基隆市', D(2026,10,23),'童子瑋', 0.7,'鏡新聞民調童子瑋反超 0.7 個百分點','','poll'),
 ('基隆市', D(2026,10,23),'謝國樑', -0.4,'過半受訪者認同「換人做做看」','','poll'),
]

def phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))

def days(a,b): return (b-a).days

def daterange(a,b):
    d=a
    while d<=b:
        yield d; d+=dt.timedelta(days=1)

def seeded(name):
    return random.Random(sum(ord(ch)*(i+1) for i,ch in enumerate(name)))

out = {'prev_national':PREV_NATIONAL,'method':{},'start':START.isoformat(),'today':TODAY.isoformat(),'eday':EDAY.isoformat(),'races':{},'national':[]}
DATES=list(daterange(START,TODAY))

# ===== 民調方法 AI 查核 =====
# 逐份讀過民調公布的方法說明後，依「抽樣框、加權、揭露程度、未表態比例、題目」評分。
# fr: dual=市話＋手機雙底冊, land=只打市話, tel=電話但未說明市話/手機, web=網路問卷, ai=AI 模擬, none=方法未揭露
# wt: 有說明加權, disc: 2 完整揭露 / 1 部分 / 0 幾乎沒有, und: 未表態 %, qw: 公布題目, fl: skew=樣本政黨傾向失衡、adv=業配或政黨挑選公布
# 新增民調時，用 (縣市, 調查結束日) 當 key 補一筆；沒補的會以「部分揭露、未知抽樣框」處理。
AUDIT={
 ('台北市','2026-09-18'):dict(fr='dual',wt=True,disc=2,und=None,qw=False,fl=[],note='市話 70%＋手機 30% 雙底冊、CATI、性別／區域／年齡／教育多變數加權，方法是這批裡最完整的之一；但主辦協會立場偏綠，題目原文未公布。'),
 ('台北市','2026-10-07'):dict(fr='land',wt=True,disc=2,und=11,qw=True,fl=[],note='市話尾數隨機、拒訪率 12.8%、多變數加權、未表態僅 11%，程序嚴謹；只打市話，年輕族群代表性不足，可能讓藍營數字偏高。'),
 ('台北市','2026-10-17'):dict(fr='none',wt=None,disc=0,und=None,qw=False,fl=[],note='報導只有結果，沒有樣本數、抽樣框、加權與調查日期；同一機構一個月內從差 1 點變成差 17 點，變動幅度遠超過抽樣誤差，可信度低。'),
 ('台北市','2026-10-25','聯合報'):dict(fr='dual',wt=True,disc=2,und=13,qw=False,fl=[],note='市話＋手機尾數隨機抽樣（補唯手機族）、性別／年齡／行政區加權，成功 1115 份、拒訪 264 人（約 19%）；題目原文未公布，訪問分 10/20–22 與 10/25 兩段。'),
 ('台北市','2026-10-25','ETtoday'):dict(fr='web',wt=True,disc=2,und=8.7,qw=False,fl=[],note='東森自建會員資料庫分層抽樣、簡訊／EDM 邀請填網路問卷，非機率樣本；性別／年齡／行政區／教育 raking 加權，樣本 1462，題目原文未公布。'),
 ('台北市','2026-10-19'):dict(fr='land',wt=True,disc=2,und=None,qw=False,fl=[],note='CATI 市話、區域／性別／年齡／教育加權、樣本 1074，程序完整；只打市話。「一定投票」者沈 51.2 比 38.6，顯示動員差異。（重新核對：題目原文、未表態比例未公布；只打住宅電話。）'),
 ('台北市','2026-05-25'):dict(fr='land',wt=True,disc=1,und=None,qw=False,fl=[],note='TVBS 例行電訪，方法沿用其標準程序；距今較久，權重已大幅衰減。'),
 ('台北市','2026-06-21'):dict(fr='tel',wt=None,disc=1,und=None,qw=False,fl=[],note='報導未完整列出抽樣與加權；時間較早，權重低。'),
 ('新北市','2026-08-26'):dict(fr='land',wt=None,disc=1,und=26,qw=False,fl=['skew'],note='住宅電話簿＋尾數隨機分層抽樣，但未提加權；樣本政黨認同民進黨 30.4%、國民黨 17.9%，明顯偏綠，李四川陣營也提出質疑。'),
 ('新北市','2026-10-03'):dict(fr='tel',wt=None,disc=1,und=19.9,qw=False,spn=False,fl=['adv'],note='由國民黨議會黨團挑選公布，抽樣框與加權未說明；TVBS 執行品質通常穩定，但「委託方決定公不公布」本身就有選擇偏誤。（重新核對：抽樣框、加權、題目都未提，委託方也未說明。）'),
 ('新北市','2026-10-10'):dict(fr='none',wt=None,disc=0,und=None,qw=False,fl=[],note='調查日期、樣本數、抽樣框、加權全部未揭露，只能當參考訊號；與同期其他民調方向相反，差距 13 點也偏大。'),
 ('新北市','2026-06-06'):dict(fr='tel',wt=None,disc=1,und=None,qw=False,fl=['adv'],note='國民黨議會黨團委託並公布，方法揭露有限；時間較早。'),
 ('桃園市','2026-10-26'):dict(fr='ai',wt=True,disc=2,und=15.0,qw=False,fl=[],note='第四波 AI 矽基樣本模擬（GPT-5.4 mini 扮演 13,789 位選民），依性別／年齡／教育／過去政黨票加權並做黨派偏差後處理；報告自承不是真實民調、可能放大媒體敘事、低估冷感選民。'),
 ('桃園市','2026-09-29'):dict(fr='ai',wt=None,disc=1,und=None,qw=False,fl=[],note='用大型語言模型扮演選民的「矽基樣本」，不是真的問人；沒有對實際選舉結果做過驗證，樣本數再大也不等於準確。'),
 ('台中市','2026-09-12'):dict(spn=False,fr='none',wt=None,disc=0,und=None,qw=False,fl=['adv'],note='國民黨議會黨團公布，報導沒有任何方法資訊（日期、樣本、抽樣、加權皆無）。'),
 ('台中市','2026-10-04'):dict(fr='tel',wt=True,disc=1,und=29.7,qw=False,fl=[],note='CATI 分層抽樣、性別／年齡／行政區加權；未表態近 3 成，雙方數字都偏低，差距的不確定性較大。（重新核對：抽樣框未說明市話或手機、題目為轉述。）'),
 ('台中市','2026-05-12'):dict(fr='tel',wt=None,disc=1,und=None,qw=False,fl=[],note='時間較早，方法揭露有限。'),
 ('台中市','2026-10-16'):dict(fr='tel',wt=True,disc=1,und=None,qw=False,fl=['adv'],note='學術單位執行、多變數加權，但由國民黨黨團委託，且刊登頁面標示為廣告；未表態約 3 成。（重新核對：抽樣框、未表態比例、題目都未公布，三人合計只有 69.5%。）'),
 ('台南市','2026-10-15'):dict(fr='land',wt=True,disc=2,und=17,qw=False,fl=['adv'],note='市話、加權、公布題目，程序完整；但由凱達格蘭基金會出資的智庫執行，屬綠營自家民調，差距 37 點明顯大於基本盤推估。（重新核對：只打市話、題目原文未公布；凱達格蘭基金會出資，由智庫挑選發布。）'),
 ('高雄市','2026-10-25'):dict(fr='web',wt=True,disc=1,und=12.7,qw=False,spn=False,fl=[],note='東森自建會員資料庫分層比例抽樣、EDM／簡訊邀請填網路問卷，非機率樣本；依性別／年齡／行政區／教育加權，樣本 1338；題目原文與出資者未說明。ETtoday 網路民調在台北也比電話民調偏藍，高雄結果和其他民調差距很大。'),
 ('高雄市','2026-08-30'):dict(fr='web',wt=None,disc=1,und=12.5,qw=False,fl=[],note='以 EDM／簡訊邀請填答的網路問卷，屬非機率樣本，未說明加權；結果與同期電話民調差距大。'),
 ('高雄市','2026-10-19'):dict(fr='ai',wt=None,disc=1,und=None,qw=False,fl=[],note='AI 矽基樣本模擬，以 2024 年選民結構為底，沒有實際受訪者，無法驗證。（重新核對：未公布整體未表態比例與模型名稱。）'),
 ('高雄市','2026-04-29'):dict(fr='tel',wt=None,disc=1,und=None,qw=False,fl=[],note='樣本 2027 較大；時間很早，權重已衰減。'),
 ('高雄市','2026-06-10'):dict(fr='land',wt=True,disc=1,und=None,qw=False,fl=[],note='綠營智庫電訪，時間較早。'),
 ('高雄市','2026-08-08'):dict(spn=False,fr='none',wt=None,disc=0,und=None,qw=False,fl=[],note='機構與方法都未載明，參考價值很低。'),
 ('基隆市','2026-08-24'):dict(fr='tel',wt=True,disc=1,und=None,qw=False,fl=[],note='山水市話電訪，媒體委託；時間較早。（重新核對：抽樣框、未表態比例、題目未公布。）'),
 ('基隆市','2026-10-09'):dict(fr='land',wt=True,disc=2,und=None,qw=False,fl=['adv','skew'],note='電話簿＋尾數隨機、raking 加權；國民黨市黨部委託，且未公布原始未表態比例，報導指樣本中民進黨支持者多於國民黨。（重新核對：只公布換算後的得票率，原始未表態比例與題目未公布。）'),
 ('基隆市','2026-10-21'):dict(fr='land',wt=True,disc=2,und=25.9,qw=True,fl=[],note='依行政區比例抽市話、raking 加權、候選人順序隨機、公布題目，程序是這批裡最嚴謹的之一；未表態 25.9%，兩人差距在誤差內。'),
 ('新竹縣','2026-10-26'):dict(fr='land',wt=True,disc=1,und=15.9,qw=False,spn=False,fl=[],note='只打市話（中華電信住宅電話尾數隨機、分層比例抽樣），匯流報導寫有加權但聯合報版本沒提；由「台灣公共政策學會」等團體記者會公布，委託出資者不明；題目原文、朱定瑀支持度都沒公布；純市話通常偏向年長、偏藍。'),
 ('新竹縣','2026-10-18'):dict(fr='web',wt=True,disc=1,und=11.2,qw=False,fl=['adv'],note='網路主動發放、非機率樣本，競辦委託並公布；有性別／年齡／居住地加權但未公布題目，網路族群可能偏綠。'),
 ('新竹縣','2026-09-21'):dict(fr='web',wt=True,disc=1,und=None,qw=False,fl=['adv'],note='同一系列 9 月波次，數字由競辦公布的增減推算，非機率樣本。'),
 ('新竹縣','2026-09-18'):dict(fr='tel',wt=True,disc=1,und=29.2,qw=False,fl=[],note='分層隨機抽樣、性別／年齡／鄉鎮加權、公布題目；未表態近 3 成，部分鄉鎮樣本只有個位數。（重新核對：抽樣框未說明、題目只轉述片段。）'),
 ('新竹縣','2026-06-16'):dict(fr='land',wt=True,disc=1,und=None,qw=False,fl=[],note='年代例行電訪，時間較早。'),
 ('彰化縣','2026-10-15'):dict(fr='tel',wt=None,disc=1,und=42,qw=False,fl=[],note='聯合報系執行品質一向穩定，但這次報導未列抽樣框與加權；未表態高達 42%，排名可信、差距不穩。'),
 ('新竹市','2026-05-20'):dict(fr='tel',wt=None,disc=1,und=None,qw=False,fl=[],note='時間很早，方法揭露有限。'),
 ('嘉義市','2026-05-03'):dict(fr='land',wt=True,disc=1,und=None,qw=False,fl=[],note='時間很早，報導僅列結果。'),
 ('嘉義市','2026-07-12'):dict(fr='tel',wt=None,disc=1,und=None,qw=False,fl=[],note='媒體轉述，抽樣與加權未完整說明。'),
 ('宜蘭縣','2026-05-02'):dict(spn=False,fr='none',wt=None,disc=0,und=None,qw=False,fl=['adv'],note='藍白整合用的協調民調，執行機構與方法都未公開。'),
 ('台東縣','2026-05-28'):dict(fr='tel',wt=None,disc=1,und=None,qw=False,fl=[],note='兩人對決題、樣本 905 偏小，時間較早。'),
 ('台北市','2026-10-22'):dict(fr='dual',wt=True,disc=2,und=None,qw=False,fl=[],note='全國 1075 人電訪（市話 696＋手機 379 雙底冊）、raking 加權，但題目原文與各分區未表態比例都沒公布；而且這是「台北＋新北」分區的政黨執政偏好，不是候選人對決，分區樣本只有約 112 人，且戴立安民調長期比同期他家偏綠，只以低權重參考。'),
 ('新北市','2026-10-22'):dict(fr='dual',wt=True,disc=2,und=None,qw=False,fl=[],note='全國 1075 人電訪（市話 696＋手機 379 雙底冊）、raking 加權，但題目原文與各分區未表態比例都沒公布；而且這是「台北＋新北」分區的政黨執政偏好，不是候選人對決，分區樣本只有約 183 人，且戴立安民調長期比同期他家偏綠，只以低權重參考。'),
 ('桃園市','2026-10-22'):dict(fr='dual',wt=True,disc=2,und=None,qw=False,fl=[],note='全國 1075 人電訪（市話 696＋手機 379 雙底冊）、raking 加權，但題目原文與各分區未表態比例都沒公布；而且這是「桃園」分區的政黨執政偏好，不是候選人對決，分區樣本只有約 101 人，且戴立安民調長期比同期他家偏綠，只以低權重參考。'),
 ('台中市','2026-10-22'):dict(fr='dual',wt=True,disc=2,und=None,qw=False,fl=[],note='全國 1075 人電訪（市話 696＋手機 379 雙底冊）、raking 加權，但題目原文與各分區未表態比例都沒公布；而且這是「台中」分區的政黨執政偏好，不是候選人對決，分區樣本只有約 125 人，且戴立安民調長期比同期他家偏綠，只以低權重參考。'),
 ('台南市','2026-10-22'):dict(fr='dual',wt=True,disc=2,und=None,qw=False,fl=[],note='全國 1075 人電訪（市話 696＋手機 379 雙底冊）、raking 加權，但題目原文與各分區未表態比例都沒公布；而且這是「台南＋高雄」分區的政黨執政偏好，不是候選人對決，分區樣本只有約 85 人，且戴立安民調長期比同期他家偏綠，只以低權重參考。'),
 ('高雄市','2026-10-22'):dict(fr='dual',wt=True,disc=2,und=None,qw=False,fl=[],note='全國 1075 人電訪（市話 696＋手機 379 雙底冊）、raking 加權，但題目原文與各分區未表態比例都沒公布；而且這是「台南＋高雄」分區的政黨執政偏好，不是候選人對決，分區樣本只有約 126 人，且戴立安民調長期比同期他家偏綠，只以低權重參考。'),
 ('基隆市','2026-10-18'):dict(fr='land',wt=True,disc=1,und=None,qw=False,spn=False,fl=['adv'],note='市話分層比例抽樣、依行政區／年齡／性別加權、樣本 1070，程序有交代；但由謝國樑競辦挑選公布，未表態比例與題目未公開，只打市話也偏向年長選民，可能高估謝國樑。（重新核對：原為「智庫內部參考」，委託智庫與出資者未說明。）'),
 ('花蓮縣','2026-10-18'):dict(fr='tel',wt=True,disc=1,und=33.5,qw=False,fl=[],note='分層隨機抽樣、依性別／戶籍／年齡／教育加權、樣本 1068；未說明是否含手機、題目未公布；未表態 33.5%，三人差距可信度有限。（重新核對：抽樣框未說明。）'),
 ('花蓮縣','2026-07-23'):dict(fr='tel',wt=None,disc=1,und=29.2,qw=False,fl=[],note='CATI、樣本 1068，但抽樣框、加權、題目都未公布；未表態近 3 成。'),
}
FR_W={'dual':1.10,'land':0.92,'tel':0.95,'web':1.0,'ai':1.0,'none':0.9}
FR_N={'dual':'市話＋手機','land':'只打市話','tel':'電話（未說明手機）','web':'網路問卷','ai':'AI 模擬','none':'方法未揭露'}
# 透明度（0–100）：資料揭露越完整分數越高；不透明的民調權重大幅調低（Jay 10/28 要求）
TR_ITEMS=[('樣本數',15),('原始報告數字',10),('抽樣框',15),('加權方式',15),('未表態比例',10),('題目原文',15),('委託者',10),('完整方法說明',10)]
def transparency(p,a):
    pts=[15 if p.get('n') and not p.get('est') else 0,
         0 if p.get('est') else 10,
         0 if a['fr']=='none' else 15,
         15 if a['wt'] else 10 if a['wt'] is False else 0,
         10 if a.get('und') is not None else 0,
         15 if a.get('qw') else 0,
         0 if a.get('spn') is False or a['fr']=='none' else 10,
         {2:10,1:4,0:0}[a['disc']]]
    return sum(pts),[n for (n,_),x in zip(TR_ITEMS,pts) if x==0]
def tr_factor(t): return round(0.3+0.7*(t/100)**1.5,3)
def audit_q(a):
    # 方法本身的品質（抽樣框、未表態、樣本失衡、業配）；揭露程度另由透明度處理
    q=FR_W[a['fr']]
    u=a.get('und'); q*=1.0 if u is None else 0.85 if u>=40 else 0.92 if u>=30 else 0.97 if u>=20 else 1.0
    if 'skew' in a['fl']: q*=0.9
    if 'adv' in a['fl']: q*=0.95
    return round(q,3)
for p in P:
    a=next((v for k,v in AUDIT.items() if len(k)==3 and k[:2]==(p['r'],p['fe'].isoformat()) and k[2] in p['org']),None) or AUDIT.get((p['r'],p['fe'].isoformat()),dict(fr='tel' if p['t']=='phone' else p['t'] if p['t']=='ai' else 'web',wt=None,disc=1,und=None,qw=False,fl=[],note='方法說明尚未查核。'))
    p['au']=a; p['qm']=audit_q(a); p['tr'],p['trmiss']=transparency(p,a); p['tf']=tr_factor(p['tr'])
    p['q']=round(max(0.25,min(1.15,p['qm']*p['tf'])),3)

# ===== 民調校正 1：機構偏差（house effect）=====
# 同一縣市、前後 45 天內，拿每家機構的「綠營減藍營」差距和其他機構的加權平均比；
# 多次比較的平均偏差再做收縮（k/(k+2)，比較次數少就不太相信），最後從該機構數字中扣掉。
HOUSES=['皮爾森','雨晴','信民','TVBS','年代','山水','大地','匯流','新台灣國策','ETtoday','TPOC','趨勢','聯合報','鉅聞','關鍵','世新','風傳媒','震傳媒','藍白合']
def house(org):
    if '戴立安' in org: return '信民'   # 同一位設計者（戴立安），視為同一機構估偏差
    for h in HOUSES:
        if h in org: return '山水' if h=='震傳媒' else h
    return org
CANDS={county:{c[0]:c for c in cfg['c']} for county,cfg in R.items()}
def gmb(p):
    cs=CANDS[p['r']]; tot=sum(p['v'].values())
    g=sum(v for n,v in p['v'].items() if n in cs and cs[n][1]=='D')
    b=sum(v for n,v in p['v'].items() if n in cs and camp(n,cs[n][1])=='B')
    return None if (not g or not b) else (g-b)/tot*100
HE_RAW={}
for p in P:
    m=gmb(p)
    if m is None or p['t']=='party': continue   # 政黨偏好題和候選人對決題問法不同，不拿來估機構偏差
    others=[q for q in P if q['r']==p['r'] and q is not p and q['t']!='party' and house(q['org'])!=house(p['org']) and abs((q['fe']-p['fe']).days)<=45 and gmb(q) is not None]
    if not others: continue
    ws=[TYPE_W[q['t']]*q['q']*math.exp(-abs((q['fe']-p['fe']).days)/40) for q in others]
    ref=sum(w*gmb(q) for w,q in zip(ws,others))/sum(ws)
    HE_RAW.setdefault(house(p['org']),[]).append((m-ref,p['q']))
# 方法分數高的民調，在推估機構偏差時說話比較大聲；收縮項 2 不變
HOUSE_EFFECT={h:round(sum(d*q for d,q in v)/(sum(q for d,q in v)+2),2) for h,v in HE_RAW.items()}
for p in P:
    he=HOUSE_EFFECT.get(house(p['org']),0.0); cs=CANDS[p['r']]; tot=sum(p['v'].values())
    p['he']=he if gmb(p) is not None else 0.0
    p['vc']={n:(v-p['he']/2*tot/100 if n in cs and cs[n][1]=='D' else v+p['he']/2*tot/100 if n in cs and camp(n,cs[n][1])=='B' else v) for n,v in p['v'].items()}

# ===== 民調校正 3：趨勢一致性 =====
# 每份民調「公布的數字」和同縣市前後 45 天、其他機構（已校正偏差）的加權共識比，得到 dev。
# 原始差距（dev）和扣掉機構偏差後的差距（res）都超過 5 點，才開始降權（最低 0.6）。
def gmb_c(p): m=gmb(p); return None if m is None else m-p['he']
for p in P:
    m=gmb(p); p['dev']=None; p['res']=None; p['cf']=1.0
    if m is None: continue
    others=[q for q in P if q['r']==p['r'] and house(q['org'])!=house(p['org']) and abs((q['fe']-p['fe']).days)<=45 and gmb(q) is not None]
    if not others: continue
    ws=[TYPE_W[q['t']]*q['q']*(0.7 if q.get('sp') else 1)*math.exp(-abs((q['fe']-p['fe']).days)/40) for q in others]
    ref=sum(w*gmb_c(q) for w,q in zip(ws,others))/sum(ws)
    p['dev']=round(m-ref,2); p['res']=round(m-p['he']-ref,2); d=min(abs(p['dev']),abs(p['res']))  # 原始或校正後任一符合共識就不降權
    p['cf']=1.0 if d<=5 else round(max(0.6,math.exp(-(d-5)/12)),3)
# ===== 民調校正 2：樣本數 =====
def size_w(p):
    return math.sqrt(min(max(p['n'],400),2000)/1000) if p.get('n') else 0.8

def run(names,party,prior,polls,evs):
    # 每日輿情指數：只由新聞事件構成（短期衝擊＋長尾），沒有事件就是 0
    buzz={n:[] for n in names}
    for n in names:
        for d in DATES:
            shock=sum(e[3]*(0.7*math.exp(-days(e[1],d)/5.5)+0.3*math.exp(-days(e[1],d)/43)) for e in evs if e[2]==n and d>=e[1])
            v=max(-1,min(1,shock)) if n!='其他' else 0.0
            buzz[n].append(round(v,3))
    series=[]
    for i,d in enumerate(DATES):
        avail=[p for p in polls if p['rel']<=d]
        acc={n:0.0 for n in names}; wsum=0.0; used=[]
        for p in avail:
            age=days(p['fe'],d)
            w=TYPE_W[p['t']]*(0.7 if p.get('sp') else 1.0)*size_w(p)*p['q']*p['cf']*math.exp(-age/40)
            named=[n for n in names if n in p['vc']]
            tot_named=sum(p['vc'][n] for n in named)
            prior_named=sum(prior[n] for n in named)
            # 民調只含部分候選人時，未列名者沿用基準占比
            for n in names:
                if n in p['vc']:
                    acc[n]+=w*(p['vc'][n]/tot_named*prior_named)
                else:
                    acc[n]+=w*prior[n]
            wsum+=w; used.append(round(w,3))
        if wsum>0:
            pollavg={n:acc[n]/wsum for n in names}
            pw=min(0.85,wsum/(wsum+0.5))
        else:
            pollavg=None; pw=0.0
        base={n:(pw*pollavg[n]+(1-pw)*prior[n]) if pollavg else prior[n] for n in names}
        # 聲量調整：7 日滾動平均淨聲量，相對於全體平均，每單位 ±1.8 個百分點，上限 ±2.5
        adj={}
        roll={n:sum(buzz[n][max(0,i-6):i+1])/len(buzz[n][max(0,i-6):i+1]) for n in names}
        real=[n for n in names if n!='其他']
        mean=sum(roll[n] for n in real)/len(real)
        for n in names:
            adj[n]=0.0 if n=='其他' else max(-2.5,min(2.5,1.8*(roll[n]-mean)))
        sh={n:max(0.3,base[n]+adj[n]) for n in names}
        s=sum(sh.values()); sh={n:sh[n]*100/s for n in names}
        order=sorted(names,key=lambda n:-sh[n])
        lead,sec=order[0],order[1]
        m=sh[lead]-sh[sec]
        s0=6.0 if wsum>0 else 8.5
        sigma=math.sqrt(s0**2+0.12*days(d,EDAY))
        wp=phi(m/sigma)
        series.append(dict(d=d.isoformat(), og=margin_og(sh,party), s={n:round(sh[n],2) for n in names}, adj={n:round(adj[n],2) for n in names},
                           pa={n:round(pollavg[n],2) for n in names} if pollavg else None, pw=round(pw,3),
                           lead=lead, m=round(m,2), wp=round(wp,4)))
    return buzz, series

# ===== 基準校正：2022 結果＋全國擺盪（uniform swing）=====
# 有民調的縣市，算出「民調差距 − 2022 差距」，依民調權重平均成全國擺盪；
# 每個縣市的 AI 基準再往「2022 差距＋全國擺盪」移一半，兩種基準各占一半。
def m22_of(county):
    pv=PREV[county]; tops=[pv['w'],pv['r']]
    g=[x[2] for x in tops if x[1]=='D']; o=[x[2] for x in tops if x[1]!='D']
    return round(max(o)-max(g),2) if g and o else None
SW=[]
for county,cfg in R.items():
    names=[c[0] for c in cfg['c']]; party={c[0]:c[1] for c in cfg['c']}
    prior={c[0]:c[2] for c in cfg['c']}
    _, ser = run(names,party,prior,[p for p in P if p['r']==county],[])
    pa=ser[-1]['pa']; m22=m22_of(county)
    if pa and m22 is not None:
        og=margin_og(pa,party)
        if og is not None: SW.append((og-m22, ser[-1]['pw']))
SWING=round(sum(a*w for a,w in SW)/sum(w for a,w in SW),2)
def prior_blend(names,party,prior,county):
    m22=m22_of(county); ogp=margin_og(prior,party)
    if m22 is None or ogp is None: return dict(prior), None
    target=m22+SWING; delta=(target-ogp)*0.5
    g=max((n for n in names if party[n]=='D'),key=lambda n:prior[n])
    o=max((n for n in names if party[n]!='D' and n!='其他'),key=lambda n:prior[n])
    pr=dict(prior); pr[o]=max(1,pr[o]+delta/2); pr[g]=max(1,pr[g]-delta/2)
    return pr, round(target,2)

for county,cfg in R.items():
    names=[c[0] for c in cfg['c']]; party={c[0]:c[1] for c in cfg['c']}
    prior_ai={c[0]:c[2] for c in cfg['c']}
    prior, fund_og = prior_blend(names,party,prior_ai,county)
    polls=[p for p in P if p['r']==county]
    evs=[e for e in EV if e[0]==county]
    buzz, series = run(names,party,prior,polls,evs)
    # 每則新聞的影響：拿掉這則新聞重算一次，兩者相減＝這則新聞讓該候選人得票率變動幾點
    evout=[]
    for e in evs:
        if e[1] not in DATES: continue
        _, wo = run(names,party,prior,polls,[x for x in evs if x is not e])
        i0=DATES.index(e[1])
        eff=[round(series[i]['s'][e[2]]-wo[i]['s'][e[2]],2) for i in range(i0,len(DATES))]
        evout.append(dict(d=e[1].isoformat(),n=e[2],k=e[3],t=e[4],url=e[5],ty=e[6],i0=i0,eff=eff))
    pv=PREV[county]; last=series[-1]
    to=turnout_est(county,last['wp']); el=round(pv['e']*ELECTORATE_GROWTH)
    valid=el*to/100*VALID_RATIO
    sig=math.sqrt((6.0 if any(p['rel']<=TODAY for p in polls) else 8.5)**2+0.12*days(TODAY,EDAY))
    proj={n:dict(pct=round(last['s'][n],2), votes=int(round(valid*last['s'][n]/100,-2)),
                lo=round(max(0,last['s'][n]-0.64*sig),1), hi=round(min(100,last['s'][n]+0.64*sig),1)) for n in names}
    pm={'w':pv['w'][1],'r':pv['r'][1]}
    m22 = None
    tops={pv['w'][0]:pv['w'],pv['r'][0]:pv['r']}
    g22=[x[2] for x in tops.values() if x[1]=='D']; o22=[x[2] for x in tops.values() if x[1]!='D']
    if g22 and o22: m22=round(max(o22)-max(g22),2)
    out['races'][county]=dict(cands=[{'n':n,'p':party[n],'prior':round(prior[n],2),'prior_ai':prior_ai[n],'camp':camp(n,party[n])} for n in names], fund_og=fund_og, note=cfg['note'],
        prev=dict(e=pv['e'],t=pv['t'],w=pv['w'],r=pv['r'],m=m22,note=pv.get('note')),
        turnout=dict(t=to,base=(62.0 if county=='嘉義市' else pv['t']),electorate=el,valid=int(round(valid,-2)),sig=round(sig,2)), proj=proj,
        polls=[dict(org=p['org'],house=house(p['org']),he=p['he'],fe=p['fe'].isoformat(),rel=p['rel'].isoformat(),n=p['n'],t=p['t'],sp=p.get('sp'),est=p.get('est',False),v=p['v'],url=p['url'],q=p['q'],qm=p['qm'],tr=p['tr'],tf=p['tf'],trmiss=p['trmiss'],cf=p['cf'],dev=p['dev'],res=p['res'],nd=(None if gmb_c(p) is None or m22_of(county) is None else round(-gmb_c(p)-m22_of(county)-SWING,2)),fr=p['au']['fr'],frn=FR_N[p['au']['fr']],wt=p['au']['wt'],disc=p['au']['disc'],und=p['au'].get('und'),fl=p['au']['fl'],note=p['au']['note']) for p in polls],
        base_ref=BASE_REF.get(county,[]), events=evout,
        buzz=buzz, series=series)

# 全國席次：依領先者政黨計席次，並以勝率加總為期望席次
for i,d in enumerate(DATES):
    seats={'K':0,'D':0,'T':0,'I':0}; exp={'K':0.0,'D':0.0,'T':0.0,'I':0.0}
    for county,r in out['races'].items():
        s=r['series'][i]; pmap={c['n']:c['p'] for c in r['cands']}
        seats[pmap[s['lead']]]+=1
        exp[pmap[s['lead']]]+=s['wp']
        order=sorted(s['s'],key=lambda n:-s['s'][n]); exp[pmap[order[1]]]+=1-s['wp']
    vb=vg=vt=0.0
    for county,r in out['races'].items():
        s=r['series'][i]; w=r['turnout']['valid']
        for c in r['cands']:
            if c['camp']=='B': vb+=w*s['s'][c['n']]/100
            elif c['camp']=='G': vg+=w*s['s'][c['n']]/100
        vt+=w
    out['national'].append(dict(d=d.isoformat(),seats=seats,exp={k:round(v,2) for k,v in exp.items()},vb=round(vb/vt*100,2),vg=round(vg/vt*100,2)))


# ===== 2024 總統大選以來的趨勢 =====
# 2024 總統大選各縣市得票率（賴清德 D／侯友宜 K／柯文哲 T），來源：維基百科 2024 Taiwanese presidential election
PRES24={'台北市':(38.13,38.08,23.79),'新北市':(38.59,35.17,26.24),'基隆市':(34.77,38.63,26.60),'宜蘭縣':(44.74,28.99,26.27),
 '桃園市':(35.27,34.12,30.61),'新竹縣':(27.42,37.03,35.55),'新竹市':(34.79,30.90,34.30),'苗栗縣':(28.81,41.18,30.01),
 '台中市':(37.58,32.37,30.05),'彰化縣':(38.11,32.93,28.96),'南投縣':(35.95,38.00,26.05),'雲林縣':(44.54,29.33,26.13),
 '嘉義縣':(47.69,29.28,23.03),'嘉義市':(43.26,31.40,25.34),'台南市':(50.95,25.61,23.44),'高雄市':(48.89,29.23,21.88),
 '屏東縣':(47.51,30.84,21.65),'台東縣':(27.41,49.32,23.28),'花蓮縣':(24.78,50.50,24.72),'澎湖縣':(38.60,36.63,24.76),
 '金門縣':(10.02,61.40,28.58),'連江縣':(10.52,62.67,26.81)}
# 全國走勢的各個點：vote=實際投票（得票率），pid=政黨偏好（政大選研中心，其餘為中立或無反應），fc=本站預測
TREND=[
 dict(d='2022-11-26',k='vote',lab='2022 縣市長',G=41.62,B=50.03,W=None,src='中選會（國民黨＋民進黨候選人合計）'),
 dict(d='2024-01-13',k='vote',lab='2024 總統',G=40.05,B=33.49,W=26.46,src='https://en.wikipedia.org/wiki/2024_Taiwanese_presidential_election'),
 dict(d='2024-01-13',k='party',lab='2024 立委政黨票',G=36.16,B=34.58,W=22.07,src='中選會'),
 dict(d='2024-12-31',k='pid',lab='2024 全年政黨偏好',G=32.3,B=20.5,W=11.8,src='政大選研中心（自由時報 2025 報導回推）'),
 dict(d='2025-06-30',k='pid',lab='2025 上半年政黨偏好',G=31.6,B=18.9,W=10.6,src='https://news.ltn.com.tw/news/politics/breakingnews/5100547'),
 dict(d='2025-12-31',k='pid',lab='2025 全年政黨偏好',G=30.8,B=20.1,W=10.9,src='政大選研中心（2026 年中報導回推）'),
 dict(d='2026-06-30',k='pid',lab='2026 上半年政黨偏好',G=33.8,B=21.0,W=8.8,src='https://disp.cc/b/HatePolitics/i8ht'),
]
TREND_EV=[
 ('2024-01-13','賴清德當選總統，立法院藍白合計過半'),
 ('2024-05-20','賴清德就職；國會改革法案引發青鳥行動'),
 ('2024-09-05','柯文哲因京華城案遭羈押，民眾黨支持度下滑'),
 ('2024-12-20','立法院三讀財劃法、選罷法修正，朝野對立升高'),
 ('2025-07-26','大罷免投票，24 案全數未通過'),
 ('2025-08-23','第二波罷免 7 案未通過、核三公投未達門檻'),
 ('2025-10-18','鄭麗文當選國民黨主席'),
 ('2026-11-28','2026 縣市長選舉'),
]
for c,r in out['races'].items(): r['pres24']=PRES24[c]

# ===== 2022/11 → 2026/6 銜接（每週一格，讓重播慢慢推進，不突然翻盤）=====
# 估算方式（不是民調）：各縣市差距＝2022 差距 − 全國擺盪(t) ＋ 候選人因素(t)。
#  全國擺盪：從 2022 結果線性走到 2026/6/1 模型值，2024 起再疊政大政黨偏好的起伏；
#  沒有候選人民調之前只用政黨（2022 結果＋全國政黨支持走勢）來估（Jay 10/29 要求）；
#  候選人因素（2026/6/1 和「政黨估計」的差，例如換人、藍營分裂）在該縣市第一份候選人民調前 8 週才用 S 曲線浮現。
def _dd(x): return D(*map(int,x.split('-')))
B0,B1=_dd('2022-11-26'),START
N0=out['national'][0]; NAT_SHIFT=(N0['vg']-N0['vb'])-(PREV_NATIONAL['D']-PREV_NATIONAL['K'])
PID=[(_dd('2024-01-13'),0.0),(_dd('2024-12-31'),11.8-12.8),(_dd('2025-06-30'),12.7-12.8),(_dd('2025-12-31'),10.7-12.8),(B1,0.0)]
def _interp(pts,t):
    if t<=pts[0][0]: return pts[0][1]
    for (a,x),(b,y) in zip(pts,pts[1:]):
        if t<=b: return x+(y-x)*(t-a).days/max(1,(b-a).days)
    return pts[-1][1]
def _s(x): x=max(0.0,min(1.0,x)); return x*x*(3-2*x)
FIRSTPOLL={}
for _p in P: FIRSTPOLL[_p['r']]=min(FIRSTPOLL.get(_p['r'],B1),_p['fe'],B1)
bridge=[]; t=B0
while t<B1:
    lin=(t-B0).days/(B1-B0).days; dev=_interp(PID,t); nat=NAT_SHIFT*lin+dev
    cs={}; seat={'G':0,'B':0,'O':0}
    for c,r in out['races'].items():
        R1=FIRSTPOLL.get(c,B1); R0=R1-dt.timedelta(days=56); k=_s((t-R0).days/(R1-R0).days)
        s0=r['series'][0]; m22=m22_of(c); pv=PREV[c]
        cmap={x['n']:x for x in r['cands']}
        if m22 is not None and s0['og'] is not None:
            og=m22-nat+k*(s0['og']-(m22-NAT_SHIFT))
            if og<0: side='D'; cp='G'
            elif k<0.5 and pv['w'][1]!='D': side=pv['w'][1]; cp='B' if side=='K' else 'O'   # 提名期前沿用 2022 當選人陣營
            else:
                ld=cmap.get(s0['lead'])
                if ld and ld['p']!='D': side=ld['p']; cp=ld['camp']
                else:
                    top=[x for x in (pv['w'],pv['r']) if x[1]!='D'][0]; side=top[1]; cp='B' if side=='K' else 'O'
            m=abs(og)
        else:
            ld=cmap.get(s0['lead']); side=ld['p'] if ld else pv['w'][1]; cp=ld['camp'] if ld else 'B'
            if k<0.5: side=pv['w'][1]; cp='G' if side=='D' else 'B' if side=='K' else 'O'
            m0=r['prev'].get('m') if r['prev'].get('m') is not None else s0['m']; m=abs(m0)+(s0['m']-abs(m0))*k
        seat[cp]+=1; cs[c]=[side,round(m,1)]
    bridge.append(dict(d=t.isoformat(),c=cs,seats=seat,vg=round(PREV_NATIONAL['D']+(N0['vg']-PREV_NATIONAL['D'])*lin+dev/2,2),vb=round(PREV_NATIONAL['K']+(N0['vb']-PREV_NATIONAL['K'])*lin-dev/2,2)))
    t+=dt.timedelta(days=7)
out['bridge']=bridge
out['trend']=dict(pts=TREND,ev=TREND_EV)
out['method']=dict(house={h:v for h,v in sorted(HOUSE_EFFECT.items(),key=lambda x:-abs(x[1]))},house_n={h:len(v) for h,v in HE_RAW.items()},swing=SWING,audit=[dict(r=p['r'],org=p['org'],house=house(p['org']),fe=p['fe'].isoformat(),t=p['t'],sp=p.get('sp'),q=p['q'],qm=p['qm'],tr=p['tr'],tf=p['tf'],cf=p['cf'],dev=p['dev'],res=p['res'],frn=FR_N[p['au']['fr']],disc=p['au']['disc'],und=p['au'].get('und')) for p in sorted(P,key=lambda x:x['fe'],reverse=True)])
json.dump(out,open('data.json','w'),ensure_ascii=False)
last=out['national'][-1]; print('today',last)
for c,r in out['races'].items():
    s=r['series'][-1]; f=r['series'][0]
    print(c, '9/1:',f['lead'],f['m'],f['wp'],' 今日:',s['lead'],s['m'],s['wp'], 'pw',s['pw'])
