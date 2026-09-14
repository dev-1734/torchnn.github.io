# dev-1734 Pages

`dev-1734` 조직의 **공용 GitHub Pages project site**입니다. 앱별 정책·지원 페이지와 계정 공용 파일을 한 저장소에서 관리합니다.

## 기본 주소

- 사이트 루트: https://dev-1734.github.io/torchnn.github.io/
- 정책 허브: https://dev-1734.github.io/torchnn.github.io/policy/

> 이 저장소는 조직 이전 전 `torchnn/torchnn.github.io`에서 사용하던 정적 페이지를 그대로 이어받았습니다. 저장소 이름을 유지하므로 GitHub Pages의 project-site 경로(`/torchnn.github.io`)가 URL에 포함됩니다.

## 구조
```
app-ads.txt              AdMob 퍼블리셔 인증(pub-8999074049545423) — 앱 공용.
                         크롤러가 도메인 루트에서만 찾는 서비스라면 project-site 경로 호환 여부를 별도 확인할 것.
policy/                  앱별 정책·지원 페이지
  index.html             허브(앱 목록)
  assets/style.css       공용 스타일(라이트/다크)
  <앱-slug>/{index,privacy,support}.html
```

## 앱별 URL (App Store Connect 입력용)
| 앱 | 개인정보 처리방침 | 지원 |
|---|---|---|
| 생활투자 지도 | https://dev-1734.github.io/torchnn.github.io/policy/life-invest-map/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/life-invest-map/support.html |
| 라스트 마일 | https://dev-1734.github.io/torchnn.github.io/policy/last-mile/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/last-mile/support.html |
| 이달의 재료 | https://dev-1734.github.io/torchnn.github.io/policy/monthly-ingredients/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/monthly-ingredients/support.html |
| qr_rxtx | https://dev-1734.github.io/torchnn.github.io/policy/qr_rxtx/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/qr_rxtx/support.html |
| 리얼리치 | https://dev-1734.github.io/torchnn.github.io/policy/real-rich/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/real-rich/support.html |
| 밤티 맵 | https://dev-1734.github.io/torchnn.github.io/policy/bamti-map/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/bamti-map/support.html |
| 프로의포폴 | https://dev-1734.github.io/torchnn.github.io/policy/portfolio-review/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/portfolio-review/support.html |
| 이달의 산 | https://dev-1734.github.io/torchnn.github.io/policy/monthly-mountains/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/monthly-mountains/support.html |
| 포토식스 | https://dev-1734.github.io/torchnn.github.io/policy/photo-six/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/photo-six/support.html |
| 판세 | https://dev-1734.github.io/torchnn.github.io/policy/fun-chart/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/fun-chart/support.html |
| 기영차트 | https://dev-1734.github.io/torchnn.github.io/policy/giyeong-chart/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/giyeong-chart/support.html |
| 땅따 | https://dev-1734.github.io/torchnn.github.io/policy/ddang-dda/privacy.html | https://dev-1734.github.io/torchnn.github.io/policy/ddang-dda/support.html |

## 새 앱 추가
1. `policy/<앱-slug>/`에 `index.html`, `privacy.html`, `support.html` 추가합니다.
2. `policy/index.html` 허브에 앱 카드를 추가합니다.
3. 이 README의 URL 표에 행을 추가합니다.
4. `main`에 push하면 GitHub Actions가 Pages를 자동 배포합니다.
5. 라이브 확인:
   ```bash
   curl -s -o /dev/null -w '%{http_code}\n' https://dev-1734.github.io/torchnn.github.io/policy/<slug>/privacy.html
   ```
   HTTP 200을 확인한 뒤 App Store Connect 등에 입력합니다.

## 이전 주소

조직 이전 전 사용하던 `https://torchnn.github.io/...` 주소는 더 이상 기준 주소로 사용하지 않습니다. 앱 코드, 스토어 메타데이터, 문서에는 위의 `dev-1734.github.io/torchnn.github.io/...` 주소를 사용합니다.
