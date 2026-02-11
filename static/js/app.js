document.addEventListener('DOMContentLoaded', function () {
    new Vue({
        el: '#app',
        data() {
            return {
                settingsVisible: false,
                cookies: {
                    qqMusic: '',
                    wyyMusic: ''
                },
                savingCookies: false,
                searchQuery: '',
                selectedSource: 'wyy',
                sources: [
                    { value: 'wyy', label: '网易云音乐' },
                    { value: 'qq', label: 'QQ音乐' },
                    { value: 'kugou', label: '酷狗音乐' },
                    { value: 'kuwo', label: '酷我音乐' }
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
                searchBarFixed: false,
                lastScrollTop: 0,
                // 播放器相关数据
                player: {
                    // 播放状态
                    currentSong: null,
                    // 播放列表
                    playList: [],
                    // 音频缓存
                    audioCache: {},
                    // 状态锁
                    isLoading: false
                },
                // HTML5 Audio 元素
                audioElement: null,
                // 播放器显示状态
                isPlaying: false,
                currentTime: 0,
                duration: 0,
                showPlaylist: false,
                // 区域标题
                sectionTitle: '相关搜索结果',
            }
        },
        computed: {
            currentSong() {
                return this.player.currentSong;
            },
            progressPercent() {
                if (this.duration > 0) {
                    return (this.currentTime / this.duration) * 100;
                }
                return 0;
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
                    this.$message.success('配置已保存到数据库');
                    this.settingsVisible = false;
                } catch (error) {
                    this.$message.error('保存失败，请检查网络');
                } finally {
                    this.savingCookies = false;
                }
            },
            openSong(song) {
                if (song.url.startsWith('http')) {
                    window.open(song.url, '_blank'); // 新标签页打开
                }
            },
            newDownload() {
                window.location.href = "/download"
            },
            toDownload(source, id) {
                window.location.href = "/download?source=" + source + "&id=" + id
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
            toDownloadPage() {
                window.location.href = '/download/';
            },
            async handleSearch() {
                if (!this.searchQuery.trim()) {
                    // 搜索为空时，显示排行榜
                    this.contentFlat = true;
                    this.results = [];
                    return;
                }

                // 重置页码为第一页
                this.currentPage = 1;
                this.contentFlat = false;
                this.loading = true;
                this.results = [];
                this.sectionTitle = '"' + this.searchQuery + '" 的搜索结果';

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
            handlePageChange(page) {
                this.currentPage = page;
                // 使用当前搜索条件重新搜索
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
            
            // 播放器方法
            async playMusic(song) {
                if (this.player.isLoading) {
                    return;
                }
                
                try {
                    this.player.isLoading = true;
                    
                    // 检查歌曲信息
                    if (!song || !song.id || !song.source) {
                        this.$message.error('歌曲信息不完整');
                        return;
                    }
                    
                    // 获取音频URL
                    const audioUrl = await this.getAudioUrl(song);
                    if (!audioUrl) {
                        this.$message.error('获取音频URL失败');
                        return;
                    }
                    
                    // 更新当前歌曲
                    this.player.currentSong = song;
                    
                    // 添加到播放列表（新歌曲排在第一位）
                    const existingIndex = this.player.playList.findIndex(item => item.id === song.id);
                    if (existingIndex !== -1) {
                        // 如果歌曲已存在，先移除旧的位置
                        this.player.playList.splice(existingIndex, 1);
                    }
                    // 将歌曲插入到列表开头
                    this.player.playList.unshift(song);
                    
                    // 设置音频源并播放
                    this.audioElement.src = audioUrl;
                    this.audioElement.play();
                    this.isPlaying = true;

                    this.$message({
                        message: `正在播放: ${song.title}`,
                        type: 'success',
                        duration: 2000
                    });
                } catch (error) {
                    console.error('播放音乐失败:', error);
                    this.$message.error('播放音乐失败，请检查网络');
                } finally {
                    this.player.isLoading = false;
                }
            },
            

            
            async getAudioUrl(song) {
                const cacheKey = `${song.source}-${song.id}`;
                
                // 检查缓存
                if (this.player.audioCache[cacheKey]) {
                    return this.player.audioCache[cacheKey];
                }
                
                // 调用后端API
                const response = await fetch(`/api/parse_song_url?song_id=${song.id}&source=${song.source}`);
                if (!response.ok) {
                    const errorData = await response.json();
                    console.error('获取音频URL失败:', errorData);
                    return null;
                }
                
                const data = await response.json();
                if (data.url) {
                    // 缓存音频URL
                    this.player.audioCache[cacheKey] = data.url;
                    return data.url;
                }
                
                return null;
            },
            
            playPrevious() {
                if (this.player.playList.length === 0) return;
                
                let currentIndex = this.player.playList.findIndex(song => 
                    song.id === this.player.currentSong?.id
                );
                
                if (currentIndex === -1) {
                    currentIndex = this.player.playList.length - 1;
                } else {
                    currentIndex = (currentIndex - 1 + this.player.playList.length) % this.player.playList.length;
                }
                
                this.playMusic(this.player.playList[currentIndex]);
            },
            
            playNext() {
                if (this.player.playList.length === 0) return;
                
                let currentIndex = this.player.playList.findIndex(song => 
                    song.id === this.player.currentSong?.id
                );
                
                currentIndex = (currentIndex + 1) % this.player.playList.length;
                this.playMusic(this.player.playList[currentIndex]);
            },
            
            togglePlay() {
                if (this.audioElement.paused) {
                    this.audioElement.play();
                    this.isPlaying = true;
                } else {
                    this.audioElement.pause();
                    this.isPlaying = false;
                }
            },
            
            updateProgress() {
                this.currentTime = this.audioElement.currentTime || 0;
                this.duration = this.audioElement.duration || 0;
            },

            formatTime(seconds) {
                if (!seconds || isNaN(seconds)) return '0:00';
                const mins = Math.floor(seconds / 60);
                const secs = Math.floor(seconds % 60);
                return `${mins}:${secs < 10 ? '0' + secs : secs}`;
            },
            
            removeFromPlaylist(index) {
                const removedSong = this.player.playList[index];
                if (!removedSong) return;

                // 检查是否移除的是当前播放的歌曲
                const isCurrentSong = this.player.currentSong && this.player.currentSong.id === removedSong.id;

                // 从播放列表中移除
                this.player.playList.splice(index, 1);

                // 如果移除的是当前播放的歌曲
                if (isCurrentSong) {
                    if (this.player.playList.length > 0) {
                        // 播放列表还有歌曲，播放下一首（移除后相同索引位置的歌曲，或第一首）
                        const nextIndex = index < this.player.playList.length ? index : 0;
                        this.playMusic(this.player.playList[nextIndex]);
                    } else {
                        // 播放列表为空，停止播放并隐藏播放器
                        this.audioElement.pause();
                        this.isPlaying = false;
                        this.player.currentSong = null;
                        this.showPlaylist = false;
                    }
                }
            },
            
            setVolume(volume) {
                if (this.audioElement) {
                    this.audioElement.volume = volume;
                }
            },
            

            
            seekTo(e) {
                const progressBar = e.currentTarget;
                const rect = progressBar.getBoundingClientRect();
                const pos = (e.clientX - rect.left) / rect.width;

                if (this.audioElement.duration) {
                    this.audioElement.currentTime = pos * this.audioElement.duration;
                }
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
                    console.log("topList:")
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
            },
            loadMoreSongs(item) {
                // 显示加载状态
                this.loading = true;
                this.contentFlat = false;
                this.sectionTitle = item.title;
                this.results = [];

                // 调用 API 获取更多歌曲
                fetch("/top_list/playlist/more?source=" + item.source + "&id=" + item.id, {
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
                    if (data.data && data.data.length > 0 && data.data[0].songs) {
                        this.results = data.data[0].songs;
                        this.total = this.results.length;
                    } else {
                        this.results = [];
                        this.total = 0;
                    }
                }).catch(error => {
                    console.error('Error:', error);
                    this.$message.error('加载榜单数据失败');
                }).finally(() => {
                    this.loading = false;
                });
            },
            handleScroll() {
                const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                
                // 当内容不是榜单（即搜索结果）时，才启用滚动固定功能
                if (!this.contentFlat) {
                    // 向下滚动超过200px时，固定搜索框
                    if (scrollTop > 200 && scrollTop > this.lastScrollTop) {
                        this.searchBarFixed = true;
                    }
                    // 向上滚动到顶部时，取消固定
                    else if (scrollTop <= 100) {
                        this.searchBarFixed = false;
                    }
                } else {
                    // 当显示榜单时，始终取消固定
                    this.searchBarFixed = false;
                }
                
                this.lastScrollTop = scrollTop;
            }
        },
        mounted() {
            this.connectWebSocket();
            this.fetchCookies();
            this.get_top_list('wyy'); // 默认加载网易云榜单
            
            // 初始化 HTML5 Audio 元素
            this.audioElement = new Audio();
            this.audioElement.addEventListener('ended', () => {
                this.isPlaying = false;
                this.playNext();
            });
            this.audioElement.addEventListener('timeupdate', () => {
                this.updateProgress();
            });
            this.audioElement.addEventListener('play', () => {
                this.isPlaying = true;
            });
            this.audioElement.addEventListener('pause', () => {
                this.isPlaying = false;
            });
            
            // 添加滚动事件监听器
            window.addEventListener('scroll', this.handleScroll);
        },
        beforeDestroy() {
            // 移除滚动事件监听器
            window.removeEventListener('scroll', this.handleScroll);
        },
    })
})