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
            card_loading: true,
            playerWindow: null
        },
        methods: {
            openSong(song) {
                if (song.url.startsWith('http')) {
                    window.open(song.url, '_blank'); // 新标签页打开
                } else {
                    this.$router.push(song.url); // 单页应用内部跳转
                }
            },
            newDownload() {
                window.location.href = "/download"
            },
            handleSearch() {
                if (!this.searchQuery.trim()) {
                    this.$message.warning('请输入搜索内容');
                    return;
                }
                this.contentFlat = false
                this.loading = true;
                this.results = [];

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
            async playMusic(item) {
                // 尝试通过 BroadcastChannel 通知现有标签页
                const channel = new BroadcastChannel("music_channel");
                channel.postMessage({type: "PLAY", payload: item});

                // 如果标签页可能被关闭，则重新打开
                setTimeout(() => {
                    channel.postMessage({type: "PING"});
                    setTimeout(() => {
                        // 如果未收到响应，说明标签页已关闭
                        window.open("/player", "_blank"); // 新标签页
                    }, 100);
                }, 100);
            },
            download(source, id, type_name) {
                window.location.href = "/download?source=" + source + "&id=" + id + "&type_name=" + type_name
            },
            handleImageError(e) {
                e.target.src = '../static/images/notFoundImage.png';
            },
            get_top_list() {
                this.card_loading = true
                fetch("/top_list", {
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
            }

        },
        mounted() {
            this.get_top_list()
        }
    })
})