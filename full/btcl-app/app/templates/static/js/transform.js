
                    function transformTime(timestamp) {
                        if (timestamp) {
                            var y = time.getFullYear(); //getFullYear方法以四位数字返回年份
                            var M = time.getMonth() + 1; // getMonth方法从 Date 对象返回月份 (0 ~ 11)，返回结果需要手动加一
                            var d = time.getDate(); // getDate方法从 Date 对象返回一个月中的某一天 (1 ~ 31)
                            var h = time.getHours(); // getHours方法返回 Date 对象的小时 (0 ~ 23)
                            var m = time.getMinutes(); // getMinutes方法返回 Date 对象的分钟 (0 ~ 59)
                            var s = time.getSeconds(); // getSeconds方法返回 Date 对象的秒数 (0 ~ 59)
                            return y + '-' + M + '-' + d + ' ' + h + ':' + m + ':' + s;
                        } else {
                            return '';
                        }
                    }


                    function bytesToSize(bytes) {
                           if (bytes === 0) return '0 B';
                            var k = 1024;
                            sizes = ['B','KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];
                            i = Math.floor(Math.log(bytes) / Math.log(k));
                        return (bytes / Math.pow(k, i)) + ' ' + sizes[i];
                           //toPrecision(3) 后面保留一位小数，如1.0GB                                                                                                                  //return (bytes / Math.pow(k, i)).toPrecision(3) + ' ' + sizes[i];
                    }