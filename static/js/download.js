document.addEventListener('DOMContentLoaded', function () {
    new Vue({
        el: '#app',
        data: {
            showCookieDialog: false,
            cookieForm: {
                platform: 'qqMusic',
                cookie: ''
            },
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
            updateCookie() {
                if (!this.cookieForm.platform) {
                    this.$message.error('请选择平台');
                    return;
                }
                if (!this.cookieForm.cookie) {
                    this.$message.error('请输入Cookie值');
                    return;
                }

                // 发送请求到后端更新Cookie
                fetch('/cookie/update', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        platform: this.cookieForm.platform,
                        cookie: this.cookieForm.cookie
                    })
                })
                    .then(response => response.json())
                    .then(data => {
                        if (data.msg === '修改成功') {
                            this.$message.success('Cookie更新成功');
                            this.showCookieDialog = false;
                            this.cookieForm.platform = '';
                            this.cookieForm.cookie = '';
                        } else {
                            this.$message.error(data.msg || '更新失败');
                        }
                    })
                    .catch(error => {
                        console.error('Error:', error);
                        this.$message.error('请求失败');
                    });
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
            this.get_url_params()
        }
    });
});