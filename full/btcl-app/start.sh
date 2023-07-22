LANG="zh_CN.UTF-8"
pid=`ps ax | grep main | grep python | grep -v grep | head -1 | awk '{print $1}'`
if [ "$pid" != "" ]; then
	echo $pid
	kill $pid
fi
echo '服务停止成功,开始重启服务...'
rm -rf nohup.out
touch nohup.out
nohup python main.py $1 -port=80 > nohup.out 2>&1 &
tail -f nohup.out
