# VWorld 크롤러

ArcGIS 시스템을 보안을 위해 HTTP 접근을 막아버렸다.
하지만 VWorld는 불쌍한 ArcGIS를 신경쓰지 않고 일방적으로 HTTP만을 고집했다.

이 도구는 ArcGIS Pro에서 VWorld에 있는 WFS를 가져올 수 있게끔 해준다.

## 사용법
- **VWorld API Key**에는 당연히 API Key를 넣으면 된다.
- **WFS Layer Name (VWorld)**에는 [VWorld Open API WFS](https://www.vworld.kr/dev/v4dv_wmsguide2_s001.do)에 있는 레이어 리스트에서 원하는 레이어의 WFS명을 찾아 넣어주면 된다.
- **Result Feature Name**은 최종적으로 추가될 레이어의 이름이다. 한글로된 피처명도 처리할 수 있으니 알맞게 사용하자.
- **Output GDB**는 굳이 설명이 필요한가?
- **Output Folder for JSON files**는 아무 폴더나 선택하면 된다. 이 도구는 API를 통해 JSON을 내려받고, 그 JSON을 통해 피처를 생성한다. 이 방법은 진주 서상원 선생님께서 고안하셨다.