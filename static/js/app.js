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
                currentTopListSource: 'wyy',  // 当前选中的排行榜平台
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
                // 歌词相关
                lyrics: [],
                currentLyricIndex: -1,
                showLyrics: false,
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

                    // 获取歌词
                    this.loadLyrics(song);

                    // 更新页面标题为当前播放的歌曲信息
                    document.title = `${song.title} - ${song.artist} | Song Station`;

                    // 设置媒体会话元数据（用于iOS/Android锁屏和通知栏显示）
                    if ('mediaSession' in navigator) {
                        navigator.mediaSession.metadata = new MediaMetadata({
                            title: song.title,
                            artist: song.artist,
                            album: song.album || '单曲',
                            artwork: [
                                { src: song.cover_url, sizes: '512x512', type: 'image/jpeg' }
                            ]
                        });

                        // 设置媒体会话操作处理器
                        navigator.mediaSession.setActionHandler('play', () => {
                            this.audioElement.play();
                        });
                        navigator.mediaSession.setActionHandler('pause', () => {
                            this.audioElement.pause();
                        });
                        navigator.mediaSession.setActionHandler('previoustrack', () => {
                            this.playPrevious();
                        });
                        navigator.mediaSession.setActionHandler('nexttrack', () => {
                            this.playNext();
                        });
                    }

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
                    // 恢复页面标题为歌曲信息
                    if (this.player.currentSong) {
                        document.title = `${this.player.currentSong.title} - ${this.player.currentSong.artist} | Song Station`;
                    }
                } else {
                    this.audioElement.pause();
                    this.isPlaying = false;
                    // 暂停时恢复默认页面标题
                    document.title = 'Song Station | 极简音乐下载';
                    // 暂停时清除媒体会话
                    if ('mediaSession' in navigator) {
                        navigator.mediaSession.metadata = null;
                    }
                }
            },
            
            updateProgress() {
                this.currentTime = this.audioElement.currentTime || 0;
                this.duration = this.audioElement.duration || 0;

                // 更新歌词高亮
                this.updateLyricHighlight();
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
            },

            // 歌词相关方法
            async loadLyrics(song) {
                try {
                    const response = await fetch(`/api/get_lyric?song_id=${song.id}&source=${song.source}`);
                    const data = await response.json();

                    if (data.lyric) {
                        this.lyrics = this.parseLyric(data.lyric);
                    } else {
                        this.lyrics = [];
                    }
                    this.currentLyricIndex = -1;
                } catch (error) {
                    console.error('加载歌词失败:', error);
                    this.lyrics = [];
                }
            },

            parseLyric(lyricText) {
                if (!lyricText) return [];

                const lines = lyricText.split('\n');
                const lyrics = [];
                const timeRegex = /\[(\d{2}):(\d{2})\.(\d{2,3})\]/g;

                lines.forEach(line => {
                    const matches = [...line.matchAll(timeRegex)];
                    if (matches.length > 0) {
                        const text = line.replace(timeRegex, '').trim();
                        if (text) {
                            matches.forEach(match => {
                                const minutes = parseInt(match[1]);
                                const seconds = parseInt(match[2]);
                                const milliseconds = parseInt(match[3].padEnd(3, '0'));
                                const time = minutes * 60 + seconds + milliseconds / 1000;
                                lyrics.push({ time, text });
                            });
                        }
                    }
                });

                // 按时间排序
                lyrics.sort((a, b) => a.time - b.time);
                return lyrics;
            },

            updateLyricHighlight() {
                if (this.lyrics.length === 0) return;

                const currentTime = this.currentTime;
                let index = -1;

                for (let i = 0; i < this.lyrics.length; i++) {
                    if (currentTime >= this.lyrics[i].time) {
                        index = i;
                    } else {
                        break;
                    }
                }

                if (index !== this.currentLyricIndex) {
                    this.currentLyricIndex = index;
                    this.scrollLyricToCenter();
                }
            },

            scrollLyricToCenter() {
                this.$nextTick(() => {
                    const container = this.$el.querySelector('.lyric-container');
                    const activeLine = this.$el.querySelector('.lyric-line.active');

                    if (container && activeLine) {
                        const containerHeight = container.clientHeight;
                        const lineTop = activeLine.offsetTop;
                        const lineHeight = activeLine.clientHeight;
                        const scrollTop = lineTop - containerHeight / 2 + lineHeight / 2;

                        container.scrollTo({
                            top: scrollTop,
                            behavior: 'smooth'
                        });
                    }
                });
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
                // 播放结束时恢复默认页面标题
                document.title = 'Song Station | 极简音乐下载';
                // 播放结束时清除媒体会话
                if ('mediaSession' in navigator) {
                    navigator.mediaSession.metadata = null;
                }
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