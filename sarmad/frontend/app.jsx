const { useState, useEffect, useRef, useCallback } = React;

// Recharts components
const Recharts = window.Recharts || {};
const { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceArea, AreaChart, Area } = Recharts;

// ==================== Custom Icons ====================
const IconBase = ({ children, size = 24, className = "" }) => (
    <svg
        xmlns="http://www.w3.org/2000/svg"
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
        className={className}
    >
        {children}
    </svg>
);

const Shield = (props) => (
    <IconBase {...props}>
        <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" />
    </IconBase>
);

const Activity = (props) => (
    <IconBase {...props}>
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" />
    </IconBase>
);

const Terminal = (props) => (
    <IconBase {...props}>
        <polyline points="4 17 10 11 4 5" />
        <line x1="12" y1="19" x2="20" y2="19" />
    </IconBase>
);

const Clock = (props) => (
    <IconBase {...props}>
        <circle cx="12" cy="12" r="10" />
        <polyline points="12 6 12 12 16 14" />
    </IconBase>
);

const Hash = (props) => (
    <IconBase {...props}>
        <line x1="4" y1="9" x2="20" y2="9" />
        <line x1="4" y1="15" x2="20" y2="15" />
        <line x1="10" y1="3" x2="8" y2="21" />
        <line x1="16" y1="3" x2="14" y2="21" />
    </IconBase>
);

const Search = (props) => (
    <IconBase {...props}>
        <circle cx="11" cy="11" r="8" />
        <line x1="21" y1="21" x2="16.65" y2="16.65" />
    </IconBase>
);

const Users = (props) => (
    <IconBase {...props}>
        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2" />
        <circle cx="9" cy="7" r="4" />
        <path d="M23 21v-2a4 4 0 0 0-3-3.87" />
        <path d="M16 3.13a4 4 0 0 1 0 7.75" />
    </IconBase>
);

const Target = (props) => (
    <IconBase {...props}>
        <circle cx="12" cy="12" r="10" />
        <circle cx="12" cy="12" r="6" />
        <circle cx="12" cy="12" r="2" />
    </IconBase>
);

const AlertTriangle = (props) => (
    <IconBase {...props}>
        <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" />
        <line x1="12" y1="9" x2="12" y2="13" />
        <line x1="12" y1="17" x2="12.01" y2="17" />
    </IconBase>
);

const Play = (props) => (
    <IconBase {...props}>
        <polygon points="5 3 19 12 5 21 5 3" />
    </IconBase>
);

const Video = (props) => (
    <IconBase {...props}>
        <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18" />
        <line x1="7" y1="2" x2="7" y2="22" />
        <line x1="17" y1="2" x2="17" y2="22" />
        <line x1="2" y1="12" x2="22" y2="12" />
        <line x1="2" y1="7" x2="7" y2="7" />
        <line x1="2" y1="17" x2="7" y2="17" />
        <line x1="17" y1="17" x2="22" y2="17" />
        <line x1="17" y1="7" x2="22" y2="7" />
    </IconBase>
);

const Send = (props) => (
    <IconBase {...props}>
        <line x1="22" y1="2" x2="11" y2="13" />
        <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </IconBase>
);

const RefreshCw = (props) => (
    <IconBase {...props}>
        <polyline points="23 4 23 10 17 10" />
        <polyline points="1 20 1 14 7 14" />
        <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15" />
    </IconBase>
);

const CheckCircle = (props) => (
    <IconBase {...props}>
        <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
        <polyline points="22 4 12 14.01 9 11.01" />
    </IconBase>
);

// ==================== WebSocket Hook ====================
const useWebSocket = (url) => {
    const [isConnected, setIsConnected] = useState(false);
    const [lastMessage, setLastMessage] = useState(null);
    const wsRef = useRef(null);
    const reconnectTimeoutRef = useRef(null);

    const connect = useCallback(() => {
        try {
            wsRef.current = new WebSocket(url);

            wsRef.current.onopen = () => {
                console.log('WebSocket connected');
                setIsConnected(true);
            };

            wsRef.current.onmessage = (event) => {
                const data = JSON.parse(event.data);
                setLastMessage(data);
            };

            wsRef.current.onclose = () => {
                console.log('WebSocket disconnected');
                setIsConnected(false);
                // Auto-reconnect after 3 seconds
                reconnectTimeoutRef.current = setTimeout(connect, 3000);
            };

            wsRef.current.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
        } catch (error) {
            console.error('Failed to connect:', error);
        }
    }, [url]);

    const sendMessage = useCallback((message) => {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        }
    }, []);

    useEffect(() => {
        connect();
        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    return { isConnected, lastMessage, sendMessage };
};

// ==================== Components ====================

const StatusBadge = ({ status }) => {
    const statusConfig = {
        idle: { label: 'جاهز للرصد', color: 'online' },
        analyzing: { label: 'تحليل لغوي...', color: 'analyzing' },
        searching: { label: 'بحث عكسي...', color: 'searching' },
        found: { label: 'تم ضبط الهدف', color: 'found' }
    };

    const config = statusConfig[status] || statusConfig.idle;

    return (
        <div className="flex items-center gap-3 bg-slate-800/50 p-4 rounded-xl border border-slate-700">
            <span className={`status-dot ${config.color}`}></span>
            <span className="font-medium">{config.label}</span>
        </div>
    );
};

const Console = ({ logs }) => {
    const consoleRef = useRef(null);

    useEffect(() => {
        if (consoleRef.current) {
            consoleRef.current.scrollTop = consoleRef.current.scrollHeight;
        }
    }, [logs]);

    return (
        <div className="console" ref={consoleRef}>
            {logs.length === 0 ? (
                <div className="text-slate-600 text-center py-8">
                    <Terminal size={32} className="mx-auto mb-2 opacity-30" />
                    <p>سجل العمليات فارغ</p>
                </div>
            ) : (
                logs.map((log, i) => (
                    <div key={i} className="console-line animate-fade-in">
                        <span className="console-time">
                            [{new Date(log.timestamp || Date.now()).toLocaleTimeString('en-US', { hour12: false })}]
                        </span>
                        <span className={`console-msg ${log.level || ''}`}>{log.message}</span>
                    </div>
                ))
            )}
        </div>
    );
};

const KeywordCard = ({ keywords, bigrams, isLoading }) => {
    if (isLoading) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-500 py-12">
                <div className="spinner mb-4"></div>
                <p>جاري استخراج الكلمات المفتاحية...</p>
            </div>
        );
    }

    if (!keywords || keywords.length === 0) {
        return (
            <div className="flex flex-col items-center justify-center h-full text-slate-600 py-12">
                <Search size={48} className="mb-4 opacity-30" />
                <p>بانتظار التحليل...</p>
            </div>
        );
    }

    return (
        <div className="space-y-4">
            <div className="space-y-3">
                {keywords.map((kw, i) => (
                    <div key={i} className="keyword-pill animate-slide-up" style={{ animationDelay: `${i * 100}ms` }}>
                        <Hash size={16} />
                        <span>{kw}</span>
                    </div>
                ))}
            </div>

            {bigrams && bigrams.length > 0 && (
                <div className="mt-6 pt-4 border-t border-slate-700">
                    <p className="text-sm text-slate-500 mb-3">العبارات الشائعة:</p>
                    <div className="flex flex-wrap gap-2">
                        {bigrams.slice(0, 3).map((bg, i) => (
                            <span key={i} className="text-xs bg-slate-700/50 text-slate-300 px-3 py-1 rounded-full">
                                {bg}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            <div className="mt-4 p-3 bg-blue-900/20 border border-blue-800/50 rounded-lg text-xs text-blue-300">
                <strong>ملاحظة:</strong> تم استخراج هذه الكلمات بواسطة خوارزمية Crowd Echo
            </div>
        </div>
    );
};

const TimelineChart = ({ data, searchWindow, status }) => {
    if (!data || data.length === 0) {
        return (
            <div className="h-full flex items-center justify-center text-slate-500">
                جاري تحميل البيانات...
            </div>
        );
    }

    const lowHour = searchWindow?.low_hour || 0;
    const highHour = searchWindow?.high_hour || 24;

    return (
        <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data}>
                <defs>
                    <linearGradient id="colorCount" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis
                    dataKey="hour"
                    stroke="#94a3b8"
                    tickFormatter={(h) => `${h}:00`}
                />
                <YAxis stroke="#94a3b8" />
                <Tooltip
                    contentStyle={{
                        backgroundColor: '#1e293b',
                        borderColor: '#334155',
                        color: '#f1f5f9',
                        borderRadius: '8px'
                    }}
                    labelFormatter={(h) => `الساعة ${h}:00`}
                    formatter={(value) => [`${value} تغريدة`, 'الحجم']}
                />
                {(status === 'searching' || status === 'found') && (
                    <ReferenceArea
                        x1={Math.floor(lowHour)}
                        x2={Math.ceil(highHour)}
                        strokeOpacity={0.5}
                        stroke="#10b981"
                        fill="#10b981"
                        fillOpacity={0.15}
                    />
                )}
                <Area
                    type="monotone"
                    dataKey="count"
                    stroke="#10b981"
                    strokeWidth={2}
                    fill="url(#colorCount)"
                />
            </AreaChart>
        </ResponsiveContainer>
    );
};

const TweetCard = ({ tweet, isSource = false }) => {
    const formatTime = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className={`tweet-card ${isSource ? 'source' : ''}`}>
            <div className="flex gap-3">
                <img
                    src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${tweet.author?.username || 'default'}`}
                    alt="avatar"
                    className="tweet-avatar"
                />
                <div className="flex-1 min-w-0">
                    <div className="flex justify-between items-start gap-2">
                        <div className="min-w-0">
                            <span className="font-bold text-sm text-white block truncate">
                                {tweet.author?.name || 'مستخدم'}
                            </span>
                            <span className="text-xs text-slate-500" dir="ltr">
                                {tweet.author?.username || '@user'}
                            </span>
                        </div>
                        <span className="text-xs text-slate-500 font-mono whitespace-nowrap">
                            {formatTime(tweet.created_at)}
                        </span>
                    </div>
                    <p className="text-sm text-slate-300 mt-2 leading-relaxed">{tweet.text}</p>

                    {tweet.media && tweet.media.length > 0 && (
                        <div className="mt-3 h-24 bg-black rounded-lg flex items-center justify-center border border-slate-700 relative overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-slate-800/50 to-slate-900/50 flex items-center justify-center">
                                <div className="w-12 h-12 rounded-full bg-white/10 backdrop-blur flex items-center justify-center">
                                    <Play size={20} className="text-white ml-1" />
                                </div>
                            </div>
                            <span className="absolute bottom-2 right-2 text-[10px] bg-black/70 px-2 py-1 rounded text-white">
                                {Math.floor((tweet.media[0].duration_ms || 45000) / 1000)}s
                            </span>
                        </div>
                    )}

                    <div className="flex gap-6 mt-3 text-xs text-slate-500">
                        <span>↺ {tweet.public_metrics?.retweet_count || 0}</span>
                        <span>♥ {tweet.public_metrics?.like_count || 0}</span>
                        <span>💬 {tweet.public_metrics?.reply_count || 0}</span>
                    </div>
                </div>
            </div>

            {isSource && (
                <div className="mt-4 pt-3 border-t border-red-500/30 flex items-center gap-2 text-red-400 text-sm">
                    <AlertTriangle size={16} />
                    <span className="font-bold">المصدر الأولي المحدد</span>
                </div>
            )}
        </div>
    );
};

const SourceResult = ({ tweet, iterations }) => {
    if (!tweet) {
        return (
            <div className="h-full flex flex-col items-center justify-center text-slate-600 py-12">
                <Target size={64} className="mb-4 opacity-20" />
                <p className="text-lg">النظام في وضع الاستعداد</p>
                <p className="text-sm mt-2">ابدأ التحليل للبحث عن المصدر</p>
            </div>
        );
    }

    const formatTime = (isoString) => {
        const date = new Date(isoString);
        return date.toLocaleTimeString('ar-SA', { hour12: true, hour: '2-digit', minute: '2-digit' });
    };

    return (
        <div className="source-result animate-slide-up">
            <div className="absolute top-4 left-4 bg-red-600 text-white text-xs font-bold px-3 py-1 rounded-full">
                مخالفة مؤكدة
            </div>

            <div className="flex flex-col items-center mb-6 pt-4">
                <div className="relative">
                    <img
                        src={`https://api.dicebear.com/7.x/avataaars/svg?seed=${tweet.author?.username}`}
                        className="w-20 h-20 rounded-full border-4 border-red-500/30"
                        alt="avatar"
                    />
                    <div className="absolute -bottom-1 -right-1 bg-red-500 w-6 h-6 rounded-full border-2 border-slate-900 flex items-center justify-center">
                        <AlertTriangle size={12} className="text-white" />
                    </div>
                </div>
                <h3 className="mt-4 text-xl font-bold text-white">{tweet.author?.name}</h3>
                <p className="text-slate-400" dir="ltr">{tweet.author?.username}</p>
            </div>

            <div className="space-y-3 text-sm border-t border-slate-700/50 pt-4">
                <div className="flex justify-between items-center">
                    <span className="text-slate-500">وقت النشر:</span>
                    <span className="text-emerald-400 font-mono font-bold">{formatTime(tweet.created_at)}</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-slate-500">النوع:</span>
                    <span className="text-slate-300 flex items-center gap-2">
                        <Video size={14} />
                        مقطع فيديو (الأصل)
                    </span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-slate-500">عدد التكرارات:</span>
                    <span className="text-purple-400">{iterations} تكرار</span>
                </div>
                <div className="flex justify-between items-center">
                    <span className="text-slate-500">نقاط الموثوقية:</span>
                    <span className="text-yellow-400">{(tweet.author?.reliability_score * 100).toFixed(0)}%</span>
                </div>
            </div>

            <div className="mt-4 p-3 bg-slate-800/50 rounded-lg">
                <p className="text-xs text-slate-400 mb-1">نص المنشور:</p>
                <p className="text-sm text-slate-200">{tweet.text}</p>
            </div>

            <button className="btn-danger w-full mt-6 flex items-center justify-center gap-2">
                <Send size={16} />
                تصدير تقرير للجهات المعنية
            </button>
        </div>
    );
};

const ReportForm = ({ onSubmit, isDisabled }) => {
    const [url, setUrl] = useState('https://x.com/fahad_ghost_99/status/1234567890');

    const handleSubmit = (e) => {
        e.preventDefault();
        onSubmit(url);
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-4">
            <div>
                <label className="block text-sm text-slate-400 mb-2">رابط التغريدة المبلغ عنها</label>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    className="report-input"
                    placeholder="https://x.com/username/status/..."
                    dir="ltr"
                />
            </div>
            <button
                type="submit"
                disabled={isDisabled}
                className="btn-primary w-full flex items-center justify-center gap-2"
            >
                {isDisabled ? (
                    <>
                        <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }}></div>
                        جاري التحليل...
                    </>
                ) : (
                    <>
                        <Search size={18} />
                        بدء التحليل والبحث
                    </>
                )}
            </button>
        </form>
    );
};

// ==================== Main App ====================
const App = () => {
    const [status, setStatus] = useState('idle');
    const [logs, setLogs] = useState([]);
    const [keywords, setKeywords] = useState([]);
    const [bigrams, setBigrams] = useState([]);
    const [volumeData, setVolumeData] = useState([]);
    const [searchWindow, setSearchWindow] = useState({ low_hour: 0, high_hour: 24 });
    const [sourceTweet, setSourceTweet] = useState(null);
    const [iterations, setIterations] = useState(0);
    const [tweets, setTweets] = useState([]);
    const [isNLPLoading, setIsNLPLoading] = useState(false);

    // WebSocket connection
    const wsUrl = `ws://${window.location.hostname}:8000/ws/analysis`;
    const { isConnected, lastMessage, sendMessage } = useWebSocket(wsUrl);

    // Handle WebSocket messages
    useEffect(() => {
        if (!lastMessage) return;

        switch (lastMessage.type) {
            case 'status':
                setStatus(lastMessage.status);
                if (lastMessage.status === 'analyzing') {
                    setIsNLPLoading(true);
                }
                break;

            case 'log':
                setLogs(prev => [...prev, lastMessage]);
                break;

            case 'volume':
                setVolumeData(lastMessage.data);
                break;

            case 'nlp_result':
                setKeywords(lastMessage.keywords);
                setBigrams(lastMessage.bigrams);
                setIsNLPLoading(false);
                break;

            case 'search_progress':
                setSearchWindow({
                    low_hour: lastMessage.low_hour,
                    high_hour: lastMessage.high_hour
                });
                break;

            case 'source_found':
                setSourceTweet(lastMessage.tweet);
                setIterations(lastMessage.iterations);
                break;

            case 'tweets':
                setTweets(lastMessage.data);
                break;

            case 'analysis_complete':
                // Analysis finished
                break;
        }
    }, [lastMessage]);

    // Load initial data and check for auto-start
    useEffect(() => {
        if (isConnected) {
            sendMessage({ action: 'get_tweets', limit: 50 });
            sendMessage({ action: 'get_volume' });

            // Check URL for tweet param (from MockX redirect)
            const params = new URLSearchParams(window.location.search);
            const tweetId = params.get('tweet');
            if (tweetId && status === 'idle') {
                console.log('Auto-starting analysis for tweet:', tweetId);
                // Clear param to avoid re-triggering on refresh if desired, 
                // but for now keeping it is fine or use history.replaceState
                window.history.replaceState({}, document.title, window.location.pathname);

                handleStartAnalysis(null, tweetId);
            }
        }
    }, [isConnected, sendMessage]);

    const handleStartAnalysis = (url, tweetId = null) => {
        // Reset state
        setLogs([]);
        setKeywords([]);
        setBigrams([]);
        setSourceTweet(null);
        setIterations(0);
        setSearchWindow({ low_hour: 0, high_hour: 24 });

        // Start analysis via WebSocket
        sendMessage({
            action: 'start_analysis',
            tweet_url: url,
            tweet_id: tweetId
        });
    };

    const isAnalyzing = status === 'analyzing' || status === 'searching';

    return (
        <div className="min-h-screen flex flex-col lg:flex-row">

            {/* Sidebar */}
            <aside className="w-full lg:w-80 bg-slate-900/80 backdrop-blur border-l border-slate-700/50 p-6 flex flex-col gap-6">
                {/* Logo */}
                <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center shadow-lg shadow-emerald-900/50">
                        <Shield size={24} className="text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold bg-gradient-to-r from-emerald-400 to-teal-300 bg-clip-text text-transparent">
                            سرمد
                        </h1>
                        <p className="text-xs text-slate-500">كاشف المصادر</p>
                    </div>
                </div>

                {/* Connection Status */}
                <div className="flex items-center gap-2 text-sm">
                    <span className={`status-dot ${isConnected ? 'online' : ''}`}></span>
                    <span className="text-slate-400">
                        {isConnected ? 'متصل بالخادم' : 'جاري الاتصال...'}
                    </span>
                </div>

                {/* Report Form */}
                <div className="glass-card p-4">
                    <h3 className="text-sm text-slate-400 mb-4 flex items-center gap-2">
                        <AlertTriangle size={16} />
                        نموذج الإبلاغ
                    </h3>
                    <ReportForm onSubmit={handleStartAnalysis} isDisabled={isAnalyzing || !isConnected} />
                </div>

                {/* Status */}
                <StatusBadge status={status} />

                {/* Console */}
                <div className="flex-1 min-h-0 flex flex-col">
                    <h3 className="text-sm text-slate-400 mb-3 flex items-center gap-2">
                        <Terminal size={16} />
                        سجل العمليات
                    </h3>
                    <div className="flex-1 overflow-hidden">
                        <Console logs={logs} />
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 p-4 lg:p-6 overflow-hidden flex flex-col gap-6">

                {/* Top Row: Chart + Keywords */}
                <div className="grid grid-cols-1 xl:grid-cols-3 gap-6 h-auto xl:h-[340px]">

                    {/* Timeline Chart */}
                    <div className="xl:col-span-2 glass-card p-5">
                        <div className="flex justify-between items-center mb-4">
                            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                <Clock size={20} className="text-emerald-400" />
                                النطاق الزمني للبحث
                            </h2>
                            <div className="flex items-center gap-4 text-xs font-mono text-emerald-400 bg-slate-800/50 px-3 py-2 rounded-lg">
                                <span>T_start: {searchWindow.low_hour?.toFixed(1) || '0'}h</span>
                                <span>T_end: {searchWindow.high_hour?.toFixed(1) || '24'}h</span>
                                <span>Δ: {((searchWindow.high_hour || 24) - (searchWindow.low_hour || 0)).toFixed(1)}h</span>
                            </div>
                        </div>
                        <div className="chart-container">
                            <TimelineChart
                                data={volumeData}
                                searchWindow={searchWindow}
                                status={status}
                            />
                        </div>
                    </div>

                    {/* Keywords */}
                    <div className="glass-card p-5">
                        <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                            <Hash size={20} className="text-purple-400" />
                            البصمة الدلالية
                        </h2>
                        <KeywordCard
                            keywords={keywords}
                            bigrams={bigrams}
                            isLoading={isNLPLoading}
                        />
                    </div>
                </div>

                {/* Bottom Row: Feed + Result */}
                <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 flex-1 min-h-0">

                    {/* Tweet Feed */}
                    <div className="glass-card flex flex-col overflow-hidden">
                        <div className="p-4 border-b border-slate-700/50 flex justify-between items-center">
                            <h2 className="text-lg font-bold text-white flex items-center gap-2">
                                <Users size={20} className="text-blue-400" />
                                ساحة الرصد
                            </h2>
                            <span className="text-xs text-slate-500 bg-slate-800/50 px-3 py-1 rounded-full">
                                {tweets.length} تغريدة
                            </span>
                        </div>
                        <div className="flex-1 overflow-y-auto p-4 space-y-4">
                            {tweets.slice(0, 30).map((tweet, i) => (
                                <TweetCard
                                    key={tweet.id || i}
                                    tweet={tweet}
                                    isSource={tweet.is_source && status === 'found'}
                                />
                            ))}
                            {tweets.length === 0 && (
                                <div className="text-center text-slate-600 py-12">
                                    <Users size={48} className="mx-auto mb-4 opacity-30" />
                                    <p>جاري تحميل التغريدات...</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* Source Result */}
                    <div className="glass-card p-5 flex flex-col">
                        <h2 className="text-lg font-bold text-white flex items-center gap-2 mb-4">
                            <Target size={20} className="text-red-400" />
                            نتيجة التحليل
                        </h2>
                        <div className="flex-1">
                            <SourceResult tweet={sourceTweet} iterations={iterations} />
                        </div>
                    </div>
                </div>
            </main>
        </div>
    );
};

// Render App
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
