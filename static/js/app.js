document.addEventListener('DOMContentLoaded', function () {
    new Vue({
        el: '#app',
        data: {
            showCookieDialog: false,
            searchQuery: '',
            selectedSource: 'wyy',
            sources: [
                {value: 'wyy', label: '网易云音乐'},
                {value: 'qq', label: 'QQ音乐'},
                {value: 'kugou', label: '酷狗音乐'},
                {value: 'kuwo', label: '酷我音乐'}
            ],
            topList: [],
            contentFlat: true,
            results: [],
            loading: false,
            currentPage: 1,
            pageSize: 20,
            total: 0,
            card_loading: false,
            playerWindow: null,
            mean_drawer: false,
        },
        methods: {
            openSong(song) {
                if (song.url.startsWith('http')) {
                    window.open(song.url, '_blank'); // 新标签页打开
                }
            },
            newDownload() {
                window.location.href = "/download"
            },
            toDownload(source,id){
                window.location.href = "/download?source="+source+"&id="+id
            },
            connectWebSocket() {
                // 连接WebSocket
                this.socket = io();
                this.socket.on('downloadApi', (data) => {
                    this.$notify({
                        title: '成功',
                        message: data.msg,
                        type: data.msgtype
                    });
                });


                this.socket.on('connect', () => {
                    console.log('WebSocket connected');
                });

                this.socket.on('disconnect', () => {
                    console.log('WebSocket disconnected');
                });
            },
            handleSearch() {
                if (!this.searchQuery.trim()) {
                    this.$message.warning('请输入搜索内容');
                    return;
                }
                this.contentFlat = false
                this.loading = true;
                this.results = [];

                fetch("/search/" + this.selectedSource + "/" + this.searchQuery + "/" + 1 + "/" + this.pageSize, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }).then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw err;
                        });
                    }
                    return response.json();
                }).then(data => {
                    this.results = data.data.songs
                    this.total = data.data.songCount
                    console.log(data.data)
                }).catch(error => {
                    console.error('Error:', error);
                }).finally(() => {
                    this.loading = false;
                });
            },
            getSourceTagType(source) {
                const typeMap = {
                    'wyy': 'danger',
                    'qq': 'success',
                    'kugou': 'primary',
                    'kuwo': 'warning'
                };
                return typeMap[source] || '';
            },
            getSourceName(source) {
                const sourceMap = {
                    'wyy': '网易云',
                    'qq': 'QQ音乐',
                    'kugou': '酷狗',
                    'kuwo': '酷我'
                };
                return sourceMap[source] || source;
            },
            getLevel(level) {
                const sourceMap = {
                    'standard': '标准品质',
                    'exhigh': '高品质',
                    'lossless': '无损品质',
                };
                return sourceMap[level] || level;
            },
            // getBackgroundBySource(source) {
            //     if (source === "wyy") {
            //         return {
            //             background: "rgba(237,95,128,0.6)",
            //             background: "-webkit-linear-gradient(to top, rgba(237,95,128,0.6) 20%, rgba(251,134,130,0.6)) 80%",
            //             background: "linear-gradient(to top, rgba(237,95,128,0.6) 20%, rgba(251,134,130,0.6)) 80%",
            //         }
            //     } else if (source === "qq") {
            //         return {
            //             background: 'rgba(34,193,120,0.6)',
            //             background: '-webkit-linear-gradient(to top, rgba(34,193,120,0.6) 10%, rgba(255,220,0,0.6) 40%',
            //             background: 'linear-gradient(to top, rgba(34,193,120,0.6) 10%, rgba(255,220,0,0.6)) 40%',
            //         }
            //
            //     }
            // },
            formatDuration(seconds) {
                const mins = Math.floor(seconds / 60);
                const secs = seconds % 60;
                return `${mins}:${secs < 10 ? '0' + secs : secs}`;
            },
            formatFileSize(bytes) {
                if (bytes === 0) return '0 B';
                const k = 1024;
                const sizes = ['B', 'KB', 'MB', 'GB'];
                const i = Math.floor(Math.log(bytes) / Math.log(k));
                return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
            },
            async downloadMusic(item) {

            },
            download(source, id, level) {
                fetch("/download/api?source=" + source + "&id=" + id + "&level=" + level, {
                    method: 'GET',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                }).then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw err;
                        });
                    }
                    return response.json();
                }).then(data => {
                    console.log(data)
                }).catch(error => {
                    console.error('Error:', error);
                })
            },
            handleImageError(e) {
                e.target.src = '../static/images/notFoundImage.png';
            },
            get_top_list(source) {
                this.card_loading = true
                this.contentFlat = true
                fetch("/top_list/" + source, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }).then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw err;
                        });
                    }
                    return response.json();
                }).then(data => {
                    this.topList = data.data
                    console.log(data.data)
                }).catch(error => {
                    console.error('Error:', error);
                }).finally(() => {
                    this.card_loading = false
                })
            },
            toPage(page) {
                window.location.href = page
            },
            loadData() {
                this.currentPage = this.currentPage + 1

                fetch("/search/" + this.selectedSource + "/" + this.searchQuery + "/" + this.currentPage + "/" + this.pageSize, {
                    headers: {
                        'Content-Type': 'application/json',
                    },
                }).then(response => {
                    if (!response.ok) {
                        return response.json().then(err => {
                            throw err;
                        });
                    }
                    return response.json();
                }).then(data => {
                    this.results = this.results.concat(data.data.songs)
                }).catch(error => {
                    console.error('Error:', error);
                }).finally(() => {
                    this.loading = false;
                });
            }
        },
        mounted() {
            this.connectWebSocket();
        }
    })
})