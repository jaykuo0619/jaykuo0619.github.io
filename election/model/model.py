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
 '金門縣': dict(c=[('陳玉珍','K',62),('李文良','I',14),('洪和成','I',12),('其他','I',12)], note='楊鎮浯卸任；藍營立委陳玉珍參選。'),
 '連江縣': dict(c=[('王忠銘','K',58),('曹爾元','I',42)], note='王忠銘尋求連任。'),
}

# 民調：類型 phone=電訪 online=網路 ai=AI 模擬；sponsor 標示政黨相關委託
# fe=調查結束日（未載明者以發布日前推估，est=True）, rel=發布日
P = [
 dict(r='台北市', org='信民兩岸研究協會（戴立安）／畢肯', fe=D(2026,9,18), rel=D(2026,9,22), n=1076, t='phone', v={'蔣萬安':41.7,'沈伯洋':40.5}, url='https://www.mirrormedia.mg/external/setn_1911133'),
 dict(r='台北市', org='TVBS 民調中心', fe=D(2026,10,7), rel=D(2026,10,9), n=1120, t='phone', v={'蔣萬安':49,'沈伯洋':41}, url='https://udn.com/news/story/124652/9803622'),
 dict(r='台北市', org='信民兩岸研究協會（戴立安）', fe=D(2026,10,17), rel=D(2026,10,20), n=None, t='phone', est=True, v={'沈伯洋':50.3,'蔣萬安':33.3}, url='https://news.ltn.com.tw/topic/戴立安民調'),
 dict(r='台北市', org='山水民意（震傳媒委託）', fe=D(2026,10,19), rel=D(2026,10,22), n=1074, t='phone', v={'沈伯洋':42.8,'蔣萬安':39.0}, url='https://tw.news.yahoo.com/%E5%8F%B0%E5%8C%97%E7%9C%9F%E9%80%86%E9%A2%A8%E4%BA%86-%E6%B2%88%E4%BC%AF%E6%B4%8B%E6%9C%80%E6%96%B0%E6%B0%91%E8%AA%BF%E5%86%8D%E8%B6%85%E8%BB%8A%E8%94%A3%E8%90%AC%E5%AE%89-025949927.html'),
 dict(r='新北市', org='年代民調中心', fe=D(2026,8,26), rel=D(2026,8,28), n=1070, t='phone', v={'蘇巧慧':37.8,'李四川':32.2}, url='https://www.nownews.com/news/6870016'),
 dict(r='新北市', org='TVBS 民調中心（國民黨新北議會黨團公布）', fe=D(2026,10,3), rel=D(2026,10,7), n=1210, t='phone', sp='K', v={'李四川':42.6,'蘇巧慧':35.9}, url='https://www.nownews.com/news/6881356'),
 dict(r='新北市', org='信民兩岸研究協會（戴立安）', fe=D(2026,10,10), rel=D(2026,10,13), n=None, t='phone', est=True, v={'蘇巧慧':43.1,'李四川':30.0}, url='https://cna.com.tw/news/aipl/202610130087.aspx'),
 dict(r='桃園市', org='TPOC 台灣議題研究中心（AI 矽基樣本模擬）', fe=D(2026,9,29), rel=D(2026,9,29), n=13789, t='ai', v={'張善政':47.3,'黃世杰':36.5}, url='https://www.mirrormedia.mg/external/mnews_20260930nm005'),
 dict(r='台中市', org='TVBS 民調中心（國民黨台中議會黨團公布）', fe=D(2026,9,12), rel=D(2026,9,14), n=None, t='phone', sp='K', est=True, v={'江啓臣':45.1,'何欣純':32.5}, url='https://www.nownews.com/news/6874941'),
 dict(r='台中市', org='年代民調中心', fe=D(2026,10,4), rel=D(2026,10,6), n=1068, t='phone', v={'江啓臣':37.3,'何欣純':31.3,'洪麗華':1.1}, url='https://www.nownews.com/news/6881349'),
 dict(r='台南市', org='新台灣國策智庫（凱達格蘭基金會出資）', fe=D(2026,10,15), rel=D(2026,10,21), n=1071, t='phone', sp='D', v={'陳亭妃':59.4,'謝龍介':22.6,'其他':1.0}, url='https://news.ltn.com.tw/news/politics/breakingnews/5613318'),
 dict(r='高雄市', org='ETtoday 民調雲（網路問卷）', fe=D(2026,8,30), rel=D(2026,9,11), n=1283, t='online', v={'柯志恩':43.8,'賴瑞隆':43.5}, url='https://www.storm.mg/article/11163759'),
 dict(r='高雄市', org='TPOC 台灣議題研究中心（AI 矽基樣本模擬）', fe=D(2026,10,19), rel=D(2026,10,20), n=20299, t='ai', v={'賴瑞隆':45.2,'柯志恩':35.2}, url='https://www.storm.mg/article/11174498'),
 dict(r='基隆市', org='山水民意（上報委託）', fe=D(2026,8,24), rel=D(2026,8,31), n=1068, t='phone', v={'謝國樑':38.6,'童子瑋':33.2}, url='https://www.nownews.com/news/6870740'),
 dict(r='基隆市', org='趨勢民調（國民黨基隆市黨部委託）', fe=D(2026,10,9), rel=D(2026,10,14), n=1070, t='phone', sp='K', v={'謝國樑':42.9,'童子瑋':38.3}, url='https://www.worldjournal.com/wj/story/121218/9816052'),
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
 # ---- 10/23 新增 ----
 dict(r='基隆市', org='大地民意（鏡新聞委託）', fe=D(2026,10,21), rel=D(2026,10,23), n=1075, t='phone', v={'童子瑋':37.0,'謝國樑':36.3,'魏造文':0.8}, url='https://setn.com/news/1927095'),
 dict(r='台中市', org='世新大學民調中心（國民黨台中議會黨團委託）', fe=D(2026,10,16), rel=D(2026,10,17), n=1070, t='phone', sp='K', v={'江啓臣':39.8,'何欣純':28.7,'洪麗華':1.0}, url='https://www.ettoday.net/news/20261024/3260334.htm'),
]
TYPE_W = {'phone':1.0,'online':0.6,'ai':0.35}

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
EV = [
 ('台北市', D(2026,9,22),'沈伯洋', 0.5,'信民民調差距縮至 1.2 個百分點'),
 ('台北市', D(2026,10,9),'蔣萬安', 0.4,'TVBS 民調蔣萬安領先 8 個百分點'),
 ('台北市', D(2026,10,20),'沈伯洋', 0.9,'信民民調沈伯洋反超 17 個百分點，網路熱議'),
 ('台北市', D(2026,10,21),'蔣萬安',-0.6,'《面對面》專訪「問 A 答 B」遭批'),
 ('台北市', D(2026,10,22),'沈伯洋', 0.4,'震傳媒民調沈伯洋領先 3.8 個百分點'),
 ('新北市', D(2026,10,7),'李四川', 0.5,'TVBS 民調李四川領先 6.7 個百分點'),
 ('新北市', D(2026,10,13),'蘇巧慧', 0.7,'信民民調蘇巧慧領先 13.1 個百分點'),
 ('新北市', D(2026,10,13),'李四川',-0.3,'藍營質疑民調為認知作戰，引發爭論'),
 ('台中市', D(2026,9,14),'江啓臣', 0.3,'TVBS 民調江啓臣領先 12.6 個百分點'),
 ('台南市', D(2026,10,21),'陳亭妃', 0.5,'民調大幅領先'),
 ('台南市', D(2026,10,21),'謝龍介',-0.4,'謝龍介批民調「侮辱選民」，爭議延燒'),
 ('高雄市', D(2026,9,5),'賴瑞隆',-0.5,'綠營負面新聞延燒，評論者下修評等'),
 ('高雄市', D(2026,9,11),'柯志恩', 0.5,'ETtoday 民調柯志恩小幅領先'),
 ('高雄市', D(2026,10,20),'賴瑞隆', 0.3,'TPOC 模擬賴瑞隆領先 10 個百分點'),
 ('基隆市', D(2026,10,14),'謝國樑', 0.3,'藍營委託民調謝國樑領先 4.6 個百分點'),
 ('新竹縣', D(2026,9,21),'鄭朝方', 0.6,'年代民調鄭朝方領先 6.4 個百分點'),
 ('彰化縣', D(2026,10,19),'陳素月', 0.4,'聯合報民調陳素月領先'),
 ('嘉義縣', D(2026,9,19),'蔡易餘', 0.4,'蔡英文前總統輔選'),
 ('嘉義縣', D(2026,9,27),'蔡易餘', 0.4,'賴清德總統輔選'),
 ('嘉義縣', D(2026,10,6),'吳品叡', 0.3,'在野大聯盟競總成立'),
 ('嘉義市', D(2026,10,19),'王美惠',-0.3,'幕後影響力爭議'),
 ('嘉義市', D(2026,10,20),'張啓楷',-0.2,'張啓楷提告王美惠等人，選戰轉趨負面'),
 ('台東縣', D(2026,9,20),'陳瑩', 0.5,'賴清德總統赴台東輔選'),
 ('台東縣', D(2026,10,20),'吳秀華',-1.0,'前縣長吳俊立（吳秀華家族）涉農路弊案遭約談、聲押'),
 ('台東縣', D(2026,10,21),'吳秀華',-0.6,'吳俊立交保境管，檢方抗告'),
 ('花蓮縣', D(2026,9,10),'游淑貞',-0.3,'縣府救災表現受批評，延燒至接班人'),
 ('花蓮縣', D(2026,10,13),'張峻', 0.7,'宣布童子賢出任競總主委'),
 ('澎湖縣', D(2026,10,1),'吳淑瑾',-0.3,'預期同情票未明顯出現'),
 ('宜蘭縣', D(2026,9,29),'林國漳', 0.2,'羅東掃街拜票'),
 ('台北市', D(2026,6,24),'蔣萬安', 0.4,'震傳媒民調蔣萬安領先近 28 個百分點'),
 ('台北市', D(2026,8,4),'沈伯洋', 0.5,'網路投票沈伯洋一度領先，社群熱議'),
 ('新北市', D(2026,6,8),'李四川', 0.4,'藍營公布民調李四川領先 6.2 個百分點'),
 ('新北市', D(2026,8,28),'蘇巧慧', 0.5,'年代民調蘇巧慧領先 5.6 個百分點'),
 ('高雄市', D(2026,6,12),'賴瑞隆', 0.4,'民調賴瑞隆領先近 18 個百分點'),
 ('高雄市', D(2026,8,10),'柯志恩', 0.5,'鉅聞天下民調雙方差距縮至 1.6 個百分點'),
 ('新竹縣', D(2026,6,17),'徐欣瑩', 0.3,'年代民調徐欣瑩小幅領先'),
 ('嘉義市', D(2026,7,20),'張啓楷', 0.4,'民調張啓楷差距縮至 3.5 個百分點'),
 ('台東縣', D(2026,6,1),'吳秀華', 0.4,'匯流民調吳秀華大幅領先'),
 ('花蓮縣', D(2026,7,29),'游淑貞', 0.3,'風傳媒民調游淑貞居首'),
 ('基隆市', D(2026,8,31),'童子瑋', 0.4,'上報民調：確定投票者雙方幾乎平手'),
 ('基隆市', D(2026,10,23),'童子瑋', 0.7,'鏡新聞民調童子瑋反超 0.7 個百分點'),
 ('基隆市', D(2026,10,23),'謝國樑',-0.4,'過半受訪者認同「換人做做看」'),
 ('新竹縣', D(2026,10,24),'徐欣瑩', 0.3,'竹檢搜索爭議引發「反司法介選」，評論指泛藍加速歸隊'),
]

def phi(x): return 0.5*(1+math.erf(x/math.sqrt(2)))

def days(a,b): return (b-a).days

def daterange(a,b):
    d=a
    while d<=b:
        yield d; d+=dt.timedelta(days=1)

def seeded(name):
    return random.Random(sum(ord(ch)*(i+1) for i,ch in enumerate(name)))

out = {'start':START.isoformat(),'today':TODAY.isoformat(),'eday':EDAY.isoformat(),'races':{},'national':[]}
DATES=list(daterange(START,TODAY))

for county,cfg in R.items():
    names=[c[0] for c in cfg['c']]; party={c[0]:c[1] for c in cfg['c']}
    prior={c[0]:c[2] for c in cfg['c']}
    polls=[p for p in P if p['r']==county]
    rng=seeded(county)
    # 每日聲量（估計值）：平滑隨機底噪 + 事件衝擊（半衰期約 4 天）
    buzz={n:[] for n in names}
    for n in names:
        rng=seeded(county+n)  # 每位候選人各自的亂數序列，日期延長時歷史不會變動
        level=0.0
        for d in DATES:
            level=0.8*level+0.2*rng.gauss(0,0.35)
            shock=sum(e[3]*math.exp(-days(e[1],d)/5.5) for e in EV if e[0]==county and e[2]==n and d>=e[1])
            v=max(-1,min(1,level+shock)) if n not in ('其他',) else 0.0
            buzz[n].append(round(v,3))
    series=[]
    for i,d in enumerate(DATES):
        avail=[p for p in polls if p['rel']<=d]
        acc={n:0.0 for n in names}; wsum=0.0; used=[]
        for p in avail:
            age=days(p['fe'],d)
            w=TYPE_W[p['t']]*(0.7 if p.get('sp') else 1.0)*math.exp(-age/40)
            named=[n for n in names if n in p['v']]
            tot_named=sum(p['v'][n] for n in named)
            prior_named=sum(prior[n] for n in named)
            # 民調只含部分候選人時，未列名者沿用基準占比
            for n in names:
                if n in p['v']:
                    acc[n]+=w*(p['v'][n]/tot_named*prior_named)
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
        series.append(dict(d=d.isoformat(), s={n:round(sh[n],2) for n in names}, adj={n:round(adj[n],2) for n in names},
                           pa={n:round(pollavg[n],2) for n in names} if pollavg else None, pw=round(pw,3),
                           lead=lead, m=round(m,2), wp=round(wp,4)))
    out['races'][county]=dict(cands=[{'n':n,'p':party[n],'prior':prior[n]} for n in names], note=cfg['note'],
        polls=[dict(org=p['org'],fe=p['fe'].isoformat(),rel=p['rel'].isoformat(),n=p['n'],t=p['t'],sp=p.get('sp'),est=p.get('est',False),v=p['v'],url=p['url']) for p in polls],
        base_ref=BASE_REF.get(county,[]), events=[dict(d=e[1].isoformat(),n=e[2],k=e[3],t=e[4]) for e in EV if e[0]==county],
        buzz=buzz, series=series)

# 全國席次：依領先者政黨計席次，並以勝率加總為期望席次
for i,d in enumerate(DATES):
    seats={'K':0,'D':0,'T':0,'I':0}; exp={'K':0.0,'D':0.0,'T':0.0,'I':0.0}
    for county,r in out['races'].items():
        s=r['series'][i]; pmap={c['n']:c['p'] for c in r['cands']}
        seats[pmap[s['lead']]]+=1
        exp[pmap[s['lead']]]+=s['wp']
        order=sorted(s['s'],key=lambda n:-s['s'][n]); exp[pmap[order[1]]]+=1-s['wp']
    out['national'].append(dict(d=d.isoformat(),seats=seats,exp={k:round(v,2) for k,v in exp.items()}))

json.dump(out,open('data.json','w'),ensure_ascii=False)
last=out['national'][-1]; print('today',last)
for c,r in out['races'].items():
    s=r['series'][-1]; f=r['series'][0]
    print(c, '9/1:',f['lead'],f['m'],f['wp'],' 今日:',s['lead'],s['m'],s['wp'], 'pw',s['pw'])
