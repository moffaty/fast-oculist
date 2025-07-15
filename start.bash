# В Git Bash:
cd /c/Users/user/Documents/fast-oculist/RTSPtoWebRTC/
nohup bash -c "GO111MODULE=on go run *.go" > go.log 2>&1 &
cd ..
nohup poetry run python app/main.py > python.log 2>&1 &
echo "logs go.log and python.log."
sleep 5s
start chrome "http://localhost:3000/index/" "http://localhost:8083/"  "http://192.168.1.68" "http://192.168.1.69"