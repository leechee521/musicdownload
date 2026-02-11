document.addEventListener('DOMContentLoaded', function () {
    new Vue({
        el: '#app',
        data: {
            showCookieDialog: false,
            cookies: {
                qqMusic: '',
                wyyMusic: ''
            },
            savingCookies: false,
            showHistory: false,
            progress: 0,
            currentSong: '等待下载...',
            songUrl: '',
            quality: 'lossless',
            history: [],
            historyPagination: {
                page: 1,
                per_page: 10,
                total: 0
            },
            socket: null,
            isLoading: false,
            historyLoading: false,
            reverse: true,
            activities: []
        },
        computed: {
            progressStatus() {
                if (this.progress < 30) return 'exception';
                if (this.progress < 70) return 'warning';
                return 'success';
            }
        },
        methods: {
            async fetchCookies() {
                try {
                    const response = await fetch('/cookie/get');
                    const data = await response.json();
                    this.cookies.qqMusic = data.qqMusic;
                    this.cookies.wyyMusic = data.wyyMusic;
                } catch (error) {
                    console.error('获取 Cookie 失败:', error);
                }
            },
            async saveCookies() {
                this.savingCookies = true;
                try {
                    await Promise.all([
                        fetch('/cookie/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ platform: 'qqMusic', cookie: this.cookies.qqMusic })
                        }),
                        fetch('/cookie/update', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ platform: 'wyyMusic', cookie: this.cookies.wyyMusic })
                        })
                    ]);
                    this.$message.success('Cookie 配置已保存');
                    this.showCookieDialog = false;
                } catch (error) {
                    console.error('保存 Cookie 失败:', error);
                    this.$message.error('保存失败，请重试');
                } finally {
                    this.savingCookies = false;
                }
            },
            submitForm() {
                if (!this.songUrl) {
                    this.$message.error('请输入歌曲链接或名称');
                    return;
                }

                this.isLoading = true;

                // 发送下载请求到后端
                fetch('/download', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        url: this.songUrl,
                        level: this.quality
                    })
                })
                    .then(response => {
                        if (!response.ok) {
                            return response.json().then(err => {
                                throw err;
                            });
                        }
                        return response.json();
                    })
                    .then(data => {
                        this.$message.success(data.msg || '下载任务已开始');
                        this.songUrl = '';
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        this.$message.error(error.msg || '下载失败');
                    })
                    .finally(() => {
                        this.isLoading = false;
                    });
            },
            connectWebSocket() {
                // 连接WebSocket
                this.socket = io();

                this.socket.on('progress_update', (data) => {
                    this.progress = data.progress;
                });
                this.socket.on('activities', (data) => {
                    this.activities.push(data)
                });


                this.socket.on('connect', () => {
                    console.log('WebSocket connected');
                });

                this.socket.on('disconnect', () => {
                    console.log('WebSocket disconnected');
                });
            },
            toHome() {
                window.location.href = "/"
            },
            get_url_params() {
                let url = new URL(window.location.href);
                let searchParams = new URLSearchParams(url.search);
                let source = searchParams.get('source');
                let id = searchParams.get('id');
                if (source === 'wyy') {
                    this.songUrl = "https://music.163.com/#/song?id=" + id
                } else if (source === 'qq') {
                    this.songUrl = "https://y.qq.com/n/ryqq/songDetail/" + id
                }
            }
        },
        mounted() {
            this.connectWebSocket();
            this.get_url_params();
            this.fetchCookies();
        }
    });
});