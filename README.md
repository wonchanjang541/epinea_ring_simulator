# 에피네아 반지 시뮬레이터
명령어: /에피반지 /에피보기 /에피랭킹 /에피초기화
드랍률 0.3%. 버튼 1/5/10마리.
기본 옵션 STR/DEX/INT/LUK 7, 공격력/마력 3이며 각 옵션별 -1/0/+1 랜덤.
Railway Variables: DISCORD_BOT_TOKEN=토큰
영구저장: Railway Volume을 /data에 마운트하고 DATA_DIR=/data 추가.


## v2 누적 저장 수정
- /에피반지를 다시 실행해도 기존 총 처치/반지 기록을 그대로 불러옵니다.
- 1/5/10마리 버튼을 누를 때마다 SQLite DB에 즉시 저장합니다.
- 초기화 버튼 또는 /에피초기화를 직접 실행할 때만 기록이 0으로 초기화됩니다.
- Railway 재배포 후에도 유지하려면 반드시 Volume Mount Path를 /data로 설정하세요.
- DATA_DIR=/data를 권장합니다. 코드가 /data Volume을 자동 감지하도록 보강했습니다.
