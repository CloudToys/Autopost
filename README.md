# Misskey Autoposter
간단한 Misskey (또는 CherryPick!) 전용 자동 노트 봇

⚠️ **이 봇을 사용할 때에는 봇 친화적인 서버, 또는 개인 서버에서 사용하시는 것을 권장합니다.**

버그가 있거나 도움이 필요하시다면 [@ALPINE_SECTOR@phater.live](https://phater.live/@ALPINE_SECTOR)로 알려주세요.

본 소스 코드의 수정 및 이용은 자유이나, 재배포 시애는 해당 리포지토리의 링크를 걸어주세요!

## What
Google 스프레드시트를 기반으로 지정된 문구들을 자동적으로 노트로 작성합니다.

현재 이 소스 코드를 기반으로 작동하고 있는 봇을 [여기에서 확인](https://phater.live/@Stainless)하실 수 있습니다!

## Features
* 최근 등장한 n개의 문구를 스킵할 수 있는 기능
* @멘션 시 입력된 문구 정보와 함께 즉시 문구를 출력할 수 있는 기능

## Options
config.example.josn 파일을 복사 후 config.json으로 이름 변경 후 작성해주세요.

## How
### Requirements
* Git
* Google Cloud Service Account
    * 구글 스프레드시트 연동을 위해 작업이 필요합니다. ([gspread 문서 참조](https://docs.gspread.org/en/latest/oauth2.html))
    * 생성한 Service Account 인증 json 키 파일의 위치를 config.json에 작성해주세요.
* Ubuntu 20.04+ or Windows 10+
* Python 3.10+
* Google 스프레드시트 ([예시 스프레드시트](https://docs.google.com/spreadsheets/d/1nO70lwFFkyyK8AtVE4fWO7lW7KDtM5pNudGJydTaQdk/edit))
    * 예시에서 복사본을 생성하여 수정하세요. 양식이 맞지 않으면 오류가 발생합니다.
### Clone source code
GitHub에서 소스 코드를 복사 후, 해당 디렉토리로 이동합니다.
```sh
> git clone https://github.com/Unstarrified/Autopost.git
> cd Autopost
```
### Setup venv (Optional)
프로덕션 서버에서 작동하는 경우, 아래 명령어로 venv를 설정하시는 것을 권장합니다.
```sh
> python3 -m venv .venv
# Ubuntu의 경우 가상 환경을 불러오려면 이 명령어를 실행하세요.
> source ./.venv/bin/activate
# Windows의 경우 가상 환경을 불러오려면 이 명령어를 실행하세요.
> call ./.venv/Scripts/activate
```
### Install dependencies
아래 명령어를 실행해 봇이 필요한 의존성 패키지를 설치합니다.
```sh
> pip install -r requirements.txt
```
### Run
아래 명령어를 실행하면 봇이 동작하기 시작합니다.
```sh
> python3 main.py
```
끝입니다! 계속 실행되도록 하시려면 nohup이나 systemd 등을 사용해주세요.
### Update
추후 봇 코드가 변경되어 업데이트가 필요한 경우, 아래 명령어를 실행하세요.
```sh
> git pull
```