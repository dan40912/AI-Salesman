# AI Salesman 五位角色素材生成 Prompt

這份文件用於交接給圖片生成、圖片編輯、語音設計或 TTS AI。目標是讓不同工具產出的角色仍保持同一張臉、同一套品牌人格與一致的聲音方向。

## 使用原則

1. 一次只製作一位角色，先完成並確認「身份母圖」，再製作其他素材。
2. 孫割已有確認母圖，不得重新設計：`frontend/assets/avatars/sun-ge-wall-street-v1.png`。
3. 其他角色必須是原創虛構人物，不模仿、不複製任何演員、名人、網紅或真實人物。
4. 所有衍生圖都必須把身份母圖當作 `Image 1`，使用圖片編輯而非重新文字生圖。
5. 每次只修改一個表情或動作，重複寫出不可改變的項目，降低換臉與服裝漂移。
6. 圖片不得包含文字、品牌 Logo、浮水印、電影元素或第三方商標。
7. 聲音使用原創合成聲線，不複製或暗示任何真實人物的聲音。

## 共用圖片規格

```text
Use case: photorealistic-natural
Asset type: AI Salesman web avatar
Primary request: create an original fictional Taiwanese AI sales consultant for a production web application
Style/medium: photorealistic commercial portrait photography; believable real skin texture; subtle pores and natural facial asymmetry; polished but not plastic or over-retouched
Composition/framing: portrait orientation; medium shot from waist or mid-torso upward; eye-level camera; subject centered; both shoulders visible; hands fully visible whenever included; enough margin for responsive UI cropping
Lighting/mood: soft cinematic key light with natural fill; clear eyes; professional, trustworthy, energetic
Color palette: restrained premium neutrals with one character-specific accent color
Constraints: one adult fictional person only; Taiwanese or East Asian appearance; anatomically correct face and hands; clean silhouette; no text; no logo; no watermark; no real-person likeness
Avoid: celebrity resemblance; movie recreation; exaggerated beauty filter; waxy skin; extra fingers; cropped hands; asymmetrical eyes; distorted teeth; sexualized pose; aggressive threatening expression; costume-like styling
```

建議保留一張高解析 PNG 母圖；網頁使用版本輸出 WebP。畫面比例以 4:5 為主，另準備 1:1 安全裁切。

## Prompt A：產生身份母圖

將下方 `{{角色規格}}` 替換成本文後段的個別角色設定。孫割不需要執行此步驟。

```text
Create one identity master portrait for the AI Salesman character below.

{{角色規格}}

Follow these production requirements:
- This is the permanent identity anchor for all later assets.
- Create one original fictional adult, not a real person and not a celebrity lookalike.
- Make the face distinctive and repeatable: clearly defined face shape, eyes, brows, nose, mouth, hairline, hairstyle and age cues.
- Use a natural Taiwanese or East Asian appearance without caricature.
- Show a medium portrait from mid-torso upward at eye level.
- Keep eyes toward camera with the character's neutral working expression.
- Keep clothing practical enough to reproduce across many images.
- Photorealistic commercial portrait photography with natural skin texture and realistic fabric.
- Leave crop-safe space around the head, shoulders and hands.
- No text, logo, watermark, trademark, extra person or celebrity resemblance.

Return exactly one clean identity master image. Do not create a collage or multiple variants.
```

## Prompt B：從母圖產生表情或動作

每一張素材都單獨執行一次。`Image 1` 必須是該角色已確認的身份母圖。

```text
Use case: identity-preserve
Asset type: AI Salesman avatar state
Input images: Image 1 is the approved identity master and the only identity reference
Primary request: change only {{本次要修改的表情或動作}}
Style/medium: preserve the exact photorealistic commercial portrait style of Image 1
Composition/framing: preserve the same camera position, focal length, crop, body scale and eye level as Image 1
Lighting/mood: preserve the same lighting direction, exposure, color grade and background as Image 1
Identity invariants: keep exactly the same person, face shape, apparent age, skin tone, eyes, eyebrows, nose, lips, teeth, hairline, hairstyle and body proportions
Wardrobe invariants: keep exactly the same clothing, colors, fabric, accessories and grooming
Scene invariants: keep the same background, furniture, perspective and depth of field
Constraints: one person only; natural anatomy; hands fully visible when used; no text; no logo; no watermark
Avoid: redesigning the face; changing age; changing hairstyle; changing outfit; beauty-filter skin; celebrity resemblance; extra fingers; distorted teeth; exaggerated theatrical acting

Return exactly one edited image. Do not return a collage, comparison sheet or explanation.
```

### 表情變數

| 系統值 | 替換文字 |
| --- | --- |
| `neutral` | neutral working expression, relaxed lips, steady eye contact |
| `smile` | small credible professional smile, relaxed eyes, closed or barely parted lips |
| `attentive` | attentive listening expression, slight forward engagement, calm focused eyes |
| `thinking` | thoughtful expression, gaze slightly off-center, subtle brow tension |
| `empathetic` | warm empathetic expression, softened eyes, restrained concern |
| `confident` | composed confident expression, direct gaze, subtle assured smile |
| `excited` | energetic positive expression, brighter eyes and a controlled open smile |

### 動作變數

| 系統值 | 替換文字 |
| --- | --- |
| `still` | neutral resting pose with both arms relaxed |
| `greeting` | small professional greeting gesture with one open hand |
| `nod` | clear but natural agreement nod while maintaining eye contact |
| `small_nod` | subtle reassuring nod with minimal body movement |
| `open_hand` | one open-palm explanatory gesture at chest height |
| `present_product` | professional two-hand presentation gesture toward an empty product area |
| `thinking` | one restrained thinking gesture near the chin without covering the face |
| `closing` | composed closing gesture with hands gently brought together |

## Prompt C：透明圖層素材（未來需要動態化時才使用）

```text
Use case: background-extraction
Asset type: layered 2.5D avatar component
Input images: Image 1 is the approved avatar state
Primary request: isolate only {{head / torso / left arm / right arm / foreground hand}} as a clean production cutout
Composition/framing: preserve the exact original canvas size, position, scale and alignment
Constraints: genuinely transparent background; preserve fine hair and fabric edges; no halo; no restyling; no added pixels outside the requested body part; no text or watermark
```

不要要求圖片 AI 直接輸出 PSD 或可用骨架。先產生對齊一致的 PNG 圖層，再由設計或前端工具組裝。

## 共用聲音生成 Prompt

將 `{{聲音規格}}` 與 `{{試聽台詞}}` 換成個別角色設定。若工具只有 TTS 而沒有「設計聲線」能力，仍使用下列描述作為 style instructions。

```text
Create an original synthetic voice for a fictional Taiwanese AI sales consultant.

Language and accent:
- Traditional Chinese, natural Taiwan Mandarin pronunciation.
- Use Taiwan vocabulary and phrasing.
- Avoid Mainland Mandarin erhua, broadcast-announcer exaggeration and foreign-accented Chinese.

{{聲音規格}}

Performance requirements:
- Sound like one consistent adult speaker across every clip.
- Speak conversationally, as if responding to one customer at close distance.
- Keep articulation clear without reading every punctuation mark mechanically.
- Use short natural pauses between ideas.
- Keep energy controlled; never shout, whisper seductively or sound threatening.
- Do not imitate any actor, celebrity, host, influencer or real salesperson.
- No background music, sound effects, room echo or other voices.
- Export clean mono WAV at 24 kHz or higher when the tool supports it.

Read this test line exactly in Traditional Chinese:
「{{試聽台詞}}」
```

## 五位角色規格

### 1. 孫割｜強勢成交型

圖片身份：直接使用 `frontend/assets/avatars/sun-ge-wall-street-v1.png` 作為 `Image 1`，不得重新生成母圖。

```text
Character: 孫割, fictional Taiwanese male AI closing consultant, apparent age 35–40
Sales personality: decisive, sharp, energetic and action-oriented; assertive without intimidation
Visual identity: angular oval face; defined jaw; focused almond-shaped dark eyes; straight strong brows; straight nose; controlled confident mouth; neatly combed dark side-parted hair
Wardrobe: deep navy 1990s-inspired financial executive suit, crisp light shirt, restrained burgundy-and-gold tie; premium but no visible brand
Scene: refined Manhattan-style financial office without identifiable landmarks or movie references
Accent color: burgundy and muted gold
```

```text
Voice: Taiwanese male, apparent age 35–42; medium-low pitch; firm chest resonance; clear consonants; approximately 1.08x normal conversational pace; decisive sentence endings; short strategic pauses before the key recommendation; energetic but never loud or coercive
Test line: 你真正要解決的，是現在有詢問，卻沒有穩定轉成下一步，對嗎？
```

### 2. 分析哥｜理性顧問型

```text
Character: 分析哥, fictional Taiwanese male AI decision consultant, apparent age 33–40
Sales personality: calm, precise, evidence-oriented and comfortable recommending an alternative
Visual identity: balanced rectangular-oval face; calm narrow almond eyes; tidy straight brows; straight nose; composed lips; neat short side-parted black hair; thin understated glasses
Wardrobe: charcoal jacket, pale blue shirt, no tie; clean modern consulting style without visible brand
Scene: quiet advisory desk with subtle charts or books kept out of focus
Accent color: slate blue
```

```text
Voice: Taiwanese male, apparent age 33–42; medium pitch; clean and dry tone; approximately 0.95x normal conversational pace; precise articulation; evenly spaced pauses before comparisons; emotionally steady without sounding cold or robotic
Test line: 先確認你的判斷標準；如果最重視的是成本，我會把風險和替代方案一起算給你看。
```

### 3. 腿姐｜魅力情境型

```text
Character: 腿姐, fictional Taiwanese female AI lifestyle sales consultant, apparent age 28–35
Sales personality: charismatic, warm, perceptive and imaginative while maintaining clear professional boundaries
Visual identity: soft oval face; expressive almond eyes; gently arched brows; refined natural nose; warm confident smile; healthy shoulder-length dark hair with a subtle natural wave
Wardrobe: contemporary tailored cream blazer with a muted plum inner top; elegant professional styling without revealing clothing or visible brand
Scene: refined lifestyle showroom or video consultation space with warm depth of field
Accent color: muted plum
Constraints: professional charisma only; no sexualized pose, body emphasis, flirtation or glamour-model styling
```

```text
Voice: Taiwanese female, apparent age 28–38; medium pitch with warm brightness; approximately 1.02x normal conversational pace; expressive but restrained melody; smile audible in positive scenarios; soft landing at the end of questions; never seductive, breathy or exaggerated
Test line: 想像一下，當顧客一進來就有人接住需求，你的團隊會多出多少時間做真正重要的事？
```

### 4. 誠實哥｜工程解說型

```text
Character: 誠實哥, fictional Taiwanese male AI technical sales consultant, apparent age 39–46
Sales personality: candid, technically grounded, patient and willing to state limitations
Visual identity: slightly long square face; attentive dark eyes; natural straight brows; practical nose; restrained friendly mouth; short dark hair with slight natural gray at the temples; optional simple rectangular glasses
Wardrobe: textured navy overshirt or work jacket over a light gray shirt; practical engineering style without visible brand
Scene: clean technical desk or product lab with softly blurred equipment
Accent color: steel blue
```

```text
Voice: Taiwanese male, apparent age 40–48; medium-low pitch; natural slightly textured timbre; approximately 0.92x normal conversational pace; patient explanatory rhythm; small pause before stating a limitation; trustworthy and plainspoken rather than polished like an announcer
Test line: 先講它怎麼運作，再談適不適合你；這部分做得到，但限制也要先說清楚。
```

### 5. 攤販姐｜務實親民型

```text
Character: 攤販姐, fictional Taiwanese female AI practical sales consultant, apparent age 46–55
Sales personality: approachable, street-smart, honest about value and focused on long-term trust
Visual identity: warm round-oval face; lively friendly eyes; soft natural brows; rounded nose; open sincere smile; practical short dark hair with a gentle wave and natural age detail
Wardrobe: clean earth-tone blouse, dark cardigan and refined practical apron; contemporary local shop style without stereotype or visible brand
Scene: bright, orderly Taiwanese neighborhood shop or market counter with softly blurred produce or shelves
Accent color: terracotta
Constraints: dignified and contemporary; no caricature, poverty cues, costume styling or exaggerated folk imagery
```

```text
Voice: Taiwanese female, apparent age 45–58; medium pitch with warm lower resonance; approximately 1.03x normal conversational pace; friendly everyday rhythm; clear numbers and units; light conversational warmth without slapstick or exaggerated Taiwanese accent
Test line: 咱們先算實際的，值不值得一看就知道；不一定要買貴，適合你才划算。
```

## 檔名與交付清單

每位角色使用固定 slug：`sun-ge`、`analyst-ge`、`lifestyle-jie`、`honest-ge`、`market-jie`。

```text
{slug}/source/identity-master-v1.png
{slug}/portrait/default.webp
{slug}/portrait/square.webp
{slug}/expressions/{emotion}.webp
{slug}/gestures/{gesture}.webp
{slug}/voice/voice-reference.wav
{slug}/voice/voice-spec.txt
{slug}/preview/contact-sheet.webp
```

目前先保留 Prompt，不需要一次生成全部素材。正式製作時的順序為：母圖確認 → 聲音試聽確認 → 表情 → 動作 → 透明圖層。

## 驗收 Prompt

可將母圖與任何衍生圖交給另一個具備視覺能力的 AI，使用以下指令檢查：

```text
Compare Image 2 with the approved identity master in Image 1.
Return PASS or FAIL for each item: identity, apparent age, face shape, eyes, eyebrows, nose, mouth, hairline, hairstyle, skin tone, body proportions, wardrobe, lighting, camera, crop, background, hands, anatomy, text/logo/watermark.
Treat any celebrity resemblance, face redesign, age drift, wardrobe drift, background drift, malformed hand or extra person as FAIL.
After the checklist, provide no more than three precise corrections. Do not praise the image and do not suggest a redesign.
```

聲音驗收項目：台灣華語、角色年齡感、音高、速度、停頓、情緒強度、咬字、是否像同一位說話者、是否出現真實人物模仿、背景噪音。任何一項不符就重新生成該段，不要用後製把錯誤聲線硬修成正式版。
