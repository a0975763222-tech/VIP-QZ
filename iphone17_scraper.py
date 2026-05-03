import React, { useState, useEffect } from 'react';
import { initializeApp } from 'firebase/app';
import { getAuth, signInAnonymously, onAuthStateChanged, signInWithCustomToken } from 'firebase/auth';
import { getFirestore, collection, onSnapshot, doc, setDoc } from 'firebase/firestore';
import { 
  TrendingDown, TrendingUp, RefreshCw, 
  Apple, Smartphone, ShieldCheck, Clock,
  LayoutDashboard, Zap, Target, Store
} from 'lucide-react';

// --- Firebase 配置與初始化 ---
// 優先使用環境提供的配置，若無則留空 (系統執行時會自動填入)
const firebaseConfig = typeof __firebase_config !== 'undefined' ? JSON.parse(__firebase_config) : {};
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

// 關鍵修正：App ID 必須與系統配發的一致，否則會出現權限錯誤
const appId = typeof __app_id !== 'undefined' ? __app_id : 'VIP-QZ';

const App = () => {
  const [user, setUser] = useState(null);
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastSync, setLastSync] = useState("");
  const [error, setError] = useState(null);

  // 1. 處理身份驗證 (遵循 Rule 3)
  useEffect(() => {
    const initAuth = async () => {
      try {
        if (typeof __initial_auth_token !== 'undefined' && __initial_auth_token) {
          await signInWithCustomToken(auth, __initial_auth_token);
        } else {
          await signInAnonymously(auth);
        }
      } catch (err) {
        console.error("Auth Error:", err);
        setError("身份驗證失敗，請重新整理頁面。");
      }
    };
    initAuth();
    
    // 監聽登入狀態切換
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
    });
    return () => unsubscribe();
  }, []);

  // 2. 監聽雲端數據 (遵循 Rule 1)
  useEffect(() => {
    // 必須確保 user 已登入才執行查詢
    if (!user) return;

    // 設定正確的 Firestore 路徑: /artifacts/{appId}/public/data/{collectionName}
    const pricesCollection = collection(db, 'artifacts', appId, 'public', 'data', 'iphone_prices');
    
    const unsubscribe = onSnapshot(pricesCollection, 
      (snapshot) => {
        const docs = snapshot.docs.map(doc => ({ id: doc.id, ...doc.data() }));
        // 依照型號名稱排序，確保畫面穩定
        const sortedData = docs.sort((a, b) => a.model.localeCompare(b.model));
        setData(sortedData);
        setLoading(false);
        setLastSync(new Date().toLocaleTimeString());
        setError(null);
      }, 
      (err) => {
        console.error("Firestore Permission/Query Error:", err);
        setError("讀取雲端數據時發生權限錯誤，請確認 App ID 設定。");
        setLoading(false);
      }
    );

    return () => unsubscribe();
  }, [user]);

  // 更新店內報價的功能
  const updateStorePrice = async (docId, newPrice) => {
    if (!user) return;
    try {
      const docRef = doc(db, 'artifacts', appId, 'public', 'data', 'iphone_prices', docId);
      await setDoc(docRef, { storePrice: Number(newPrice) }, { merge: true });
    } catch (err) {
      console.error("Update Error:", err);
    }
  };

  const PriceCard = ({ item }) => {
    const landmark = item.landmark || 0;
    const jiesheng = item.jiesheng || 0;
    const sogi = item.sogi || 0;
    
    // 計算市場最低價
    const prices = [landmark, jiesheng, sogi].filter(p => p > 0);
    const lowest = prices.length > 0 ? Math.min(...prices) : 0;
    
    // 店內報價 (如果雲端沒資料，預設為市場最低減 100)
    const storePrice = item.storePrice || (lowest > 0 ? lowest - 100 : 0);
    const diff = storePrice - lowest;

    return (
      <div className={`rounded-3xl border-l-[12px] p-6 shadow-2xl transition-all hover:scale-[1.02] mb-6 ${
        item.brand === 'apple' ? 'bg-slate-800 border-slate-400' : 'bg-blue-950/40 border-blue-600'
      }`}>
        <div className="flex justify-between items-start mb-6">
          <div className="flex-1">
            <h3 className="text-4xl font-black text-white leading-tight">{item.model}</h3>
            <div className="flex items-center gap-2 mt-2">
              <span className="bg-white/10 text-white/50 px-3 py-1 rounded text-xs font-bold tracking-widest uppercase">256GB VERSION</span>
            </div>
          </div>
          <div className="text-right ml-4">
            <p className="text-slate-400 text-sm font-bold mb-1 flex items-center justify-end gap-1">
              <Store size={14} /> 今日店內報價
            </p>
            <input 
              type="number"
              defaultValue={storePrice}
              onBlur={(e) => updateStorePrice(item.id, e.target.value)}
              className="bg-transparent text-5xl font-black text-blue-400 text-right focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 w-full max-w-[250px]"
            />
          </div>
        </div>

        <div className="grid grid-cols-3 gap-4 bg-black/30 rounded-2xl p-6 mb-4">
          <div className="text-center border-r border-white/10">
            <p className="text-red-400 font-bold mb-1 text-sm uppercase tracking-wider">地標網通</p>
            <p className="text-2xl font-black text-white">{landmark > 0 ? landmark.toLocaleString() : '---'}</p>
          </div>
          <div className="text-center border-r border-white/10">
            <p className="text-green-400 font-bold mb-1 text-sm uppercase tracking-wider">傑昇通信</p>
            <p className="text-2xl font-black text-white">{jiesheng > 0 ? jiesheng.toLocaleString() : '---'}</p>
          </div>
          <div className="text-center">
            <p className="text-orange-400 font-bold mb-1 text-sm uppercase tracking-wider">手機王報價</p>
            <p className="text-2xl font-black text-white">{sogi > 0 ? sogi.toLocaleString() : '---'}</p>
          </div>
        </div>

        <div className={`flex items-center justify-between px-6 py-3 rounded-full font-black text-2xl shadow-lg ${
          diff <= 0 ? 'bg-green-600/20 text-green-400 border border-green-500/30' : 'bg-red-600/20 text-red-400 border border-red-500/30'
        }`}>
          <div className="flex items-center gap-2">
            <Target size={24} className="opacity-50" />
            <span className="text-lg opacity-70">市場最低：{lowest.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-2">
            {diff <= 0 ? <TrendingDown size={28} /> : <TrendingUp size={28} />}
            <span>{diff === 0 ? '平盤' : `${diff > 0 ? '+' : ''}${diff.toLocaleString()}`}</span>
          </div>
        </div>
      </div>
    );
  };

  if (loading) return (
    <div className="h-screen bg-[#020617] flex flex-col items-center justify-center text-white">
      <RefreshCw className="animate-spin mb-6 text-blue-500" size={60} />
      <h2 className="text-3xl font-black tracking-widest animate-pulse">連線至雲端戰情室中...</h2>
      <p className="mt-4 text-slate-500">正在驗證身份與讀取報價數據</p>
    </div>
  );

  return (
    <div className="min-h-screen bg-[#020617] text-slate-100 p-8 selection:bg-blue-500 selection:text-white">
      {/* 錯誤提示區 */}
      {error && (
        <div className="mb-8 bg-red-900/50 border-2 border-red-500 text-red-200 p-6 rounded-2xl flex items-center gap-4 animate-bounce">
          <div className="bg-red-500 p-2 rounded-full"><Zap size={24} /></div>
          <div>
            <h4 className="text-xl font-bold">連線異常</h4>
            <p className="opacity-80">{error}</p>
          </div>
        </div>
      )}

      <header className="flex justify-between items-center mb-10 border-b border-white/10 pb-8">
        <div className="flex items-center gap-6">
          <div className="bg-gradient-to-br from-blue-600 to-indigo-700 p-5 rounded-3xl shadow-2xl shadow-blue-500/30">
            <LayoutDashboard size={50} className="text-white" />
          </div>
          <div>
            <h1 className="text-6xl font-black tracking-tighter">
              LIVE <span className="text-blue-500 underline decoration-4 underline-offset-8">戰情室</span>
            </h1>
            <div className="flex items-center gap-4 mt-2">
              <p className="text-slate-400 text-xl font-bold flex items-center gap-2 italic">
                <Clock size={20} /> 雲端同步：{lastSync || "等待中..."}
              </p>
              <span className="h-2 w-2 rounded-full bg-green-500 animate-pulse"></span>
              <span className="text-xs font-mono text-slate-600 uppercase tracking-widest">ID: {appId}</span>
            </div>
          </div>
        </div>
        <div className="text-right">
           <p className="text-4xl font-black tracking-tight">銓 / 昇 展 通 信</p>
           <p className="text-slate-500 font-bold tracking-[0.2em] text-lg mt-1 uppercase">SINCE 1989 | TAIWAN</p>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
        {/* Apple 區域 */}
        <div className="space-y-6">
          <div className="flex items-center gap-4 px-4 mb-4">
            <div className="p-3 bg-slate-800 rounded-2xl"><Apple fill="currentColor" size={32} className="text-slate-300" /></div>
            <h2 className="text-5xl font-black text-slate-300 tracking-tight">APPLE <span className="text-slate-600 text-2xl font-medium ml-2">旗艦戰區</span></h2>
          </div>
          {data.filter(i => i.brand === 'apple').length > 0 ? (
            data.filter(i => i.brand === 'apple').map((item, idx) => <PriceCard key={idx} item={item} />)
          ) : (
            <div className="p-10 border-2 border-dashed border-slate-800 rounded-3xl text-center text-slate-600 text-2xl font-bold">
              等待 Apple 數據推送中...
            </div>
          )}
        </div>

        {/* Samsung 區域 */}
        <div className="space-y-6">
          <div className="flex items-center gap-4 px-4 mb-4">
            <div className="p-3 bg-blue-900/30 rounded-2xl"><Smartphone size={32} className="text-blue-500" /></div>
            <h2 className="text-5xl font-black text-blue-500 tracking-tight">SAMSUNG <span className="text-blue-900 text-2xl font-medium ml-2">旗艦戰區</span></h2>
          </div>
          {data.filter(i => i.brand === 'samsung').length > 0 ? (
            data.filter(i => i.brand === 'samsung').map((item, idx) => <PriceCard key={idx} item={item} />)
          ) : (
            <div className="p-10 border-2 border-dashed border-blue-950/30 rounded-3xl text-center text-blue-900 text-2xl font-bold">
              等待 Samsung 數據推送中...
            </div>
          )}
        </div>
      </div>

      <footer className="mt-20 flex justify-between items-end border-t border-white/5 pt-10">
        <div className="text-slate-600 text-lg font-medium space-y-1">
          <p>地址：桃園市龜山區中興路 402 號</p>
          <p>電話：03-3590858 | 統編：80089553</p>
        </div>
        <div className="text-right">
          <p className="text-slate-800 text-sm font-mono uppercase tracking-[0.5em]">Security Protocol Active</p>
          <p className="text-slate-500 italic text-xl font-medium mt-2">「誠信經營，您的戰情後盾」</p>
        </div>
      </footer>
    </div>
  );
};

export default App;
