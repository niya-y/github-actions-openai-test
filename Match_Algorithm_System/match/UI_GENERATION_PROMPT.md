# 🎨 BluedonuLab UI 생성 프롬프트 (Google Stitch용)

## 프롬프트 1: 전체 앱 구조 설명

```
I need you to generate a complete UI/UX design for a healthcare caregiver matching application called "BluedonuLab".

PROJECT OVERVIEW:
- An AI-powered platform that matches patients with caregivers based on personality traits and medical needs
- Target users: Elderly patients, families, and professional caregivers
- Main goal: Find the best psychological compatibility match, not just medical compatibility

CORE FEATURES TO BUILD:

1. PATIENT FLOW:
   - Onboarding screen with welcome message
   - Personality test (12 questions about empathy, activity, patience, independence)
   - Results screen showing 4 personality trait scores (0-100 scale)
   - Caregiver recommendation screen showing top 5 matches with:
     * Caregiver profile photo
     * Name and credentials
     * Match score (0-100) with grade (A+, A, B+, B, C)
     * Key personality matches highlighted
     * Trust score visualization
   - Detailed caregiver profile page with:
     * Full background information
     * Care style description
     * Previous ratings and reviews
     * Button to request matching

2. CAREGIVER FLOW:
   - Professional profile setup screen
   - Care style questionnaire (similar to patient flow)
   - Care style profile results
   - Matched patients list with pending requests
   - Daily care report submission form
   - Schedule management calendar

3. ADMIN/FAMILY DASHBOARD:
   - Overview of all active matchings
   - Patient progress dashboard
   - Quality metrics and care reports
   - Notification center

DESIGN REQUIREMENTS:
- Modern, clean, and trustworthy design (healthcare app)
- Mobile-first responsive design
- Accessible color scheme (high contrast, colorblind friendly)
- Easy-to-understand visualizations for scores
- Warm, empathetic tone through design
- Progress indicators for multi-step flows

DATABASE INTEGRATION:
- Connect to SQLite database with these tables:
  * Residents (patients)
  * Staff (caregivers)
  * PatientPersonality (4 scores)
  * CaregiverStyle (4 scores)
  * PersonalityBasedMatching (match results)
  * DailyReport (care logs)

PLEASE GENERATE:
- Complete wireframes for all screens
- Component library with buttons, cards, input fields
- Color palette and typography system
- Interactive prototypes if possible
- Navigation flow diagrams
```

---

## 프롬프트 2: 환자 성향 테스트 UI

```
Generate an interactive personality test UI screen for a healthcare app called BluedonuLab.

REQUIREMENTS:
- Test Title: "당신의 성향을 알아보세요" (Know Your Care Preferences)
- Total: 12 questions
- Display format: Card-based, one question per screen with progress bar
- Question type: Multiple choice (3 options per question)
- Language: Korean interface

QUESTIONS TO INCLUDE:
1. "반복되는 같은 질문을 할 때 간병인이 어떻게 하길 원하나요?"
   - Options: 차분히 설명 | 참고 설명 | 빠르게 대화 전환
   - Measures: PATIENCE

2. "혼자 할 수 있는 것을 최대한 혼자 하고 싶다"
   - Options: 완전 동의 | 약간 동의 | 동의하지 않음
   - Measures: INDEPENDENCE

3. "간병인과의 감정적 유대감이 얼마나 중요한가요?"
   - Options: 매우 중요 | 어느 정도 | 중요하지 않음
   - Measures: EMPATHY

4. "하루를 어떻게 보내고 싶으신가요?"
   - Options: 활동적으로 | 적당히 | 조용히 쉬면서
   - Measures: ACTIVITY

5-12. [Similar questions for depth]

VISUAL ELEMENTS:
- Progress bar at top (e.g., "Question 3 of 12")
- Large, readable question text (font size 18+)
- Card-style answer buttons with icons
- Smooth transitions between questions
- Skip/Back/Next navigation buttons
- Estimated time to complete (3-5 minutes)

RESULT SCREEN AFTER COMPLETION:
- Show 4 radar/spider chart for scores:
  * 공감도 (Empathy): 0-100
  * 활동성 (Activity): 0-100
  * 인내심 (Patience): 0-100
  * 독립성 (Independence): 0-100
- Personality type classification (e.g., "공감 중심형 + 차분함")
- AI-generated personality description (2-3 sentences)
- "매칭된 간병인 찾기" (Find Matched Caregivers) button
```

---

## 프롬프트 3: 매칭 결과/추천 화면

```
Create a beautiful caregiver recommendation screen for BluedonuLab app.

CONTEXT:
- Patient has completed personality test
- System has calculated match scores with 1,000 caregivers
- Showing top 5 recommendations sorted by match score

SCREEN LAYOUT:
- Header: "당신을 위한 맞춤 간병인" (Personalized Caregivers for You)
- Filters: Care Level (High/Moderate/Low), Distance, Price range
- Sort options: Best Match, Highest Rating, Closest

CARD DESIGN FOR EACH CAREGIVER:
- Profile photo (circular, 80x80px)
- Name and title (e.g., "박수진 · 간병인")
- Match score badge (e.g., "78점 · B+" in green)
- 4 matching indicators with icons:
  * 🤝 공감도 일치: 85점
  * 🏃 활동성 일치: 72점
  * ⏳ 인내심 일치: 90점
  * 🦅 독립성 일치: 65점
- Star rating (e.g., ★★★★☆ 4.8, 24 reviews)
- "매칭 요청" (Request Match) button
- "프로필 보기" (View Profile) link

MATCHING SCORE COLOR CODING:
- 90-100: Dark green (A+)
- 85-89: Light green (A)
- 75-84: Yellow (B+)
- 65-74: Orange (B)
- Below 65: Red (C)

INTERACTIVE ELEMENTS:
- Tap card to see full profile
- Swipe left/right to browse
- Add to favorites (star icon)
- Share caregiver recommendation
- Chat/message button for direct contact

ADDITIONAL INFORMATION ON EACH CARD:
- Years of experience (e.g., "경력 5년")
- Availability status (Available/Busy)
- Recent review snippet (1-2 sentences)
- "이 간병인이 추천되는 이유:" section with 3 key points

DESIGN STYLE:
- Warm, trustworthy color palette
- Clear visual hierarchy
- Accessibility: High contrast text
- Smooth animations for transitions
- Empty state: Show encouraging message if no matches
```

---

## 프롬프트 4: 간병인 상세 프로필 화면

```
Generate a detailed caregiver profile screen for the BluedonuLab healthcare app.

CAREGIVER PROFILE DATA:
- Name: 박수진 (Park Su-jin)
- Title: 간병인 (Caregiver)
- Years of Experience: 5년
- Specialties: Elderly care, Daily living assistance, Patient companionship
- Location: 서울시 강남구
- Availability: Full-time, Flexible hours
- Languages: Korean, English (Basic)
- Certifications: Home Care Worker License, CPR Certified

SCREEN SECTIONS (Scrollable):

1. HERO SECTION:
   - Large profile photo
   - Name, title, location badge
   - Star rating (4.8/5)
   - Match score badge (78 · B+)
   - Quick stats: 5년 경력, 24건 리뷰, 98% 만족도

2. PERSONALITY MATCH VISUALIZATION:
   - Side-by-side comparison:
     LEFT (Patient) | MIDDLE (Match Score) | RIGHT (Caregiver)
   - 공감도: Patient 80 — 75 Caregiver (85점 일치)
   - 활동성: Patient 55 — 65 Caregiver (72점 일치)
   - 인내심: Patient 85 — 82 Caregiver (90점 일치)
   - 독립성: Patient 60 — 70 Caregiver (65점 일치)

3. ABOUT SECTION:
   - Care style description (4-5 sentences)
   - "당신과 잘 맞는 이유:" (Why You Match Well):
     * "따뜻한 감정 지원을 제공하는 스타일"
     * "차분하고 인내심 있는 소통"
     * "환자의 독립성을 존중하는 태도"

4. REVIEWS SECTION:
   - Top 3-5 recent reviews
   - Each review shows:
     * 별점 (Stars)
     * 환자 초성 (e.g., "L.S")
     * 리뷰 텍스트
     * 날짜
   - "모든 리뷰 보기" link

5. EXPERIENCE & SKILLS:
   - Care specialties (icons + text)
   - Equipment proficiency (medication assist, mobility aid, etc.)
   - Languages spoken
   - Certifications with dates

6. AVAILABILITY CALENDAR:
   - 2-week mini calendar
   - Green = available, Gray = booked
   - Time slot selection

7. PRICING:
   - Hourly rate: ₩20,000
   - Daily rate: ₩180,000
   - Monthly subscription option
   - Additional services and costs

8. ACTION BUTTONS:
   - Primary: "이 간병인과 매칭" (Request Match)
   - Secondary: "메시지 보내기" (Send Message)
   - Tertiary: "프로필 공유" (Share Profile)

DESIGN ELEMENTS:
- Gradient background for hero section
- Icon usage for quick scanning
- Trust badges (Verified, Top-rated)
- Responsive layout for mobile
- Sticky action buttons at bottom
```

---

## 프롬프트 5: 매칭 성공 후 대시보드

```
Create a post-matching patient dashboard for BluedonuLab showing active care arrangements.

DASHBOARD PURPOSE:
- Display all active matchings
- Show daily care reports
- Schedule management
- Communication hub

MAIN SECTIONS:

1. ACTIVE MATCHING CARD:
   - Caregiver profile mini (photo, name, rating)
   - Matching score recap
   - Status: "활성화 (Active)" with green badge
   - Start date and duration
   - "다음 방문: 오늘 오후 2시" (Next visit)
   - Quick action buttons:
     * 📞 전화
     * 💬 메시지
     * 📅 일정 보기

2. DAILY REPORT FEED:
   - Reverse chronological list
   - Each report shows:
     * Date and time
     * Caregiver name/photo
     * Quick health metrics:
       - 💊 복약 여부 (Medication taken)
       - 🍽️ 식사량 (Meal intake)
       - 🚶 활동량 (Activity level)
       - 😊 기분 (Mood)
     * Report summary (3-4 sentences)
     * Photos/attachments if any
     * "자세히 보기" (View Full Report) link

3. UPCOMING SCHEDULE:
   - Next 7 days calendar view
   - Color-coded by caregiver
   - Time slots and notes
   - Edit/cancel buttons

4. COMMUNICATION CENTER:
   - Unread message count
   - Latest messages from caregiver
   - Quick reply buttons
   - Full chat history link

5. QUICK STATS WIDGET:
   - Total care hours this month
   - Satisfaction rating
   - Attendance rate (%)
   - Next billing date

6. EMERGENCY/HELP BUTTONS:
   - Red button: "긴급 연락" (Emergency Contact)
   - Yellow button: "문제 보고" (Report Issue)

NOTIFICATIONS:
- Daily report posted reminder
- Upcoming visit reminder
- Message notifications
- System alerts

DESIGN STYLE:
- Clean, organized layout
- Easy-to-scan information hierarchy
- Warm, supportive color scheme
- Accessibility-focused
- Mobile-optimized with touch-friendly buttons
```

---

## 프롬프트 6: 간병인 일일 리포트 입력 화면

```
Design a daily care report submission form for caregivers in the BluedonuLab app.

CONTEXT:
- Caregiver completes this at end of care shift
- Takes 2-3 minutes to fill
- Helps family track patient's condition

FORM SECTIONS:

1. BASIC INFO (Auto-filled):
   - Date/Time
   - Patient name
   - Care duration (e.g., 2 hours 30 minutes)
   - Caregiver name

2. HEALTH METRICS (Quick selection with icons):
   ☐ 복약 (Medication)
     - 예 | 아니오 | 일부만

   ☐ 식사 (Meals)
     - 아침: 많이 | 적당히 | 조금 | 못함
     - 점심: 많이 | 적당히 | 조금 | 못함
     - 저녁: 많이 | 적당히 | 조금 | 못함

   ☐ 물섭취 (Hydration)
     - 양호 | 보통 | 부족

   ☐ 배변 (Bowel movement)
     - 정상 | 변비 | 설사 | 없음

   ☐ 수면 (Sleep)
     - 잘 자심 | 보통 | 잠을 못 주무심

   ☐ 기분 (Mood)
     - 😄 밝음 | 😐 보통 | 😞 우울 | 😤 불안

3. ACTIVITY LOG:
   - 활동 기록 (Activities):
     * Checkbox list:
       ☐ 산책 (30분)
       ☐ 스트레칭 (15분)
       ☐ 대화/사교 (1시간)
       ☐ 독서
       ☐ 텔레비전
       ☐ 취미활동
   - 거동 상태 (Mobility):
     * 정상 | 조금 불편 | 많이 불편 | 침상

4. HEALTH OBSERVATIONS:
   - 체온 (Temperature): [Input field] °C
   - 혈압 (Blood Pressure): [Input fields] /
   - 특이사항 (Special Notes):
     * Text area for detailed observations
     * Max 500 characters
     * Placeholder: "환자의 상태나 특이사항을 기록해주세요..."

5. INCIDENT REPORTING (if any):
   - 낙상 | 약물 실수 | 응급상황 | 기타
   - Detailed incident description
   - Severity level

6. PHOTO/ATTACHMENT:
   - Optional photo upload
   - (Medication confirmation, meal photos, etc.)

7. FAMILY NOTES:
   - Message to family:
     * Text area
     * @mention family members
     * Can add encouraging updates

8. QUICK TEMPLATES (for recurring reports):
   - "모두 좋습니다" (Everything is good)
   - "작은 문제 발생" (Minor issue)
   - "의료 상담 필요" (Need medical consultation)
   - [Custom templates]

BUTTONS:
- Primary: "저장 및 전송" (Save & Send) - sends to family
- Secondary: "임시 저장" (Save as Draft)
- Tertiary: "취소" (Cancel)

VALIDATION:
- Required fields highlighted
- Confirmation before sending
- Success message on submission

DESIGN:
- Large tap targets (healthcare workers may wear gloves)
- Clear section dividers
- Icons for quick visual scanning
- Light, readable typography
- Warm, encouraging tone
```

---

## 프롬프트 7: 관리자/가족 대시보드

```
Create an admin/family management dashboard for BluedonuLab showing multiple patients.

DASHBOARD OVERVIEW:
- Family members can monitor all care arrangements
- Admin can see platform-wide metrics
- Real-time notifications and alerts

MAIN SECTIONS:

1. KEY METRICS CARDS (Top):
   - 총 매칭 수 (Total Matchings): 5
   - 평균 만족도 (Avg Satisfaction): 4.8/5 ⭐
   - 이달 케어 시간 (Care Hours This Month): 120
   - 아직 읽지 않은 리포트 (Unread Reports): 3

2. PATIENT LIST VIEW (Table/Card):
   - 환자명 (Patient Name)
   - 현재 간병인 (Current Caregiver)
   - 매칭 점수 (Match Score)
   - 상태 (Status): Active/Inactive
   - 마지막 리포트 (Last Report): "2시간 전"
   - 만족도 (Satisfaction): ⭐⭐⭐⭐⭐
   - 액션: View Details, Edit Matching, View Reports

3. INDIVIDUAL PATIENT DETAIL VIEW:
   - 환자 정보 (Patient Info)
   - 현재 간병인 정보 (Current Caregiver)
   - 매칭 기간 (Matching Duration)
   - 만족도 그래프 (Satisfaction Trend) - 30일
   - 리포트 피드 (Reports Feed):
     * 최근 리포트 5개
     * Filter by date range
     * Export to PDF option

4. CAREGIVER PERFORMANCE:
   - Caregiver name and stats
   - Total matching hours
   - Average rating
   - Patient satisfaction breakdown
   - Response time metrics
   - Reliability score

5. ALERTS & NOTIFICATIONS:
   - 🔴 중요 (Critical):
     * Missing medication doses
     * Health concerns
     * Cancellations
   - 🟡 주의 (Warning):
     * Below average satisfaction
     * Late reports
     * Communication gaps
   - 🟢 정보 (Info):
     * Positive feedback
     * Milestone reached

6. QUALITY METRICS:
   - Caregiver attendance rate (%)
   - Report submission timeliness
   - Patient satisfaction scores by dimension
   - Care continuity assessment

7. FINANCIAL VIEW (if applicable):
   - Billing overview
   - Payment status
   - Invoices and receipts
   - Refund/adjustment management

8. SETTINGS & MANAGEMENT:
   - Add/remove caregivers
   - Adjust matching parameters
   - Communication templates
   - Export data

DESIGN FEATURES:
- Responsive layout (desktop, tablet, mobile)
- Dark mode option
- Multiple view options (Table, Cards, Timeline)
- Advanced filters
- Search functionality
- Customizable widgets
- Export capabilities (PDF, CSV)
```

---

## 프롬프트 8: 전체 네비게이션 & 정보 아키텍처

```
Define the complete navigation structure and information architecture for BluedonuLab app.

APP STRUCTURE:

ROOT LEVEL:
├── 🏠 홈 (Home/Dashboard)
├── 👤 프로필 (Profile)
├── 📋 매칭 (Matchings)
├── 💬 메시지 (Messages)
└── ⚙️ 설정 (Settings)

HOME TAB:
├── Welcome banner
├── Active matching card
├── Upcoming events
├── Recent activity
├── Quick actions (Request new matching, View reports)

MATCHINGS TAB:
├── Active matchings
│   ├── Matching details
│   ├── Caregiver info
│   ├── Schedule
│   └── Reports
├── Pending requests
├── Completed matchings (history)
└── Matching search & discovery
    ├── Browse available caregivers
    ├── Filters (experience, rate, location, specialty)
    ├── Personality test results
    └── Recommendations

MESSAGES TAB:
├── Conversation list
├── Search/filter conversations
├── Direct message with caregiver
├── Group messages (family + caregiver)
├── Message history

PROFILE TAB (for Patients):
├── My Information
│   ├── Personal details
│   ├── Medical conditions
│   ├── Care preferences
│   └── Emergency contacts
├── My Personality Profile
│   ├── Personality test results
│   ├── Care preferences summary
│   └── Retake test
├── Health Records
│   ├── Medical history
│   ├── Current medications
│   └── Allergies
└── Edit Profile

PROFILE TAB (for Caregivers):
├── My Information
├── My Care Style Profile
├── Certifications & Licenses
├── Availability Calendar
├── Earnings & Payments
└── Statistics & Reviews

SETTINGS TAB:
├── Account Settings
│   ├── Change password
│   ├── Two-factor authentication
│   └── Account deletion
├── Notification Preferences
│   ├── Report notifications
│   ├── Message alerts
│   ├── Matching updates
│   └── System alerts
├── Privacy & Security
│   ├── Data sharing preferences
│   ├── Connected devices
│   └── Login history
├── Communication
│   ├── Preferred language
│   ├── Contact method
│   └── Message templates
├── Accessibility
│   ├── Text size
│   ├── High contrast mode
│   ├── Screen reader support
│   └── Font selection
├── Help & Support
│   ├── FAQ
│   ├── Contact support
│   ├── Bug reports
│   └── Feature requests
└── About
    ├── App version
    ├── Terms of service
    ├── Privacy policy
    └── Acknowledgments

DEEP LINKING STRUCTURE:
/home
/matchings
/matchings/:id (specific matching)
/caregivers/browse
/caregivers/:id (caregiver profile)
/personality-test
/messages
/messages/:conversationId
/profile
/profile/edit
/settings

NAVIGATION PATTERNS:
- Tab-based main navigation (5 tabs)
- Drawer/hamburger menu for secondary options
- Back button for previous screens
- Floating action button for quick actions
  * Patient: Request new matching, Send message
  * Caregiver: Submit daily report, View schedule

USER FLOWS:

PATIENT FIRST-TIME FLOW:
1. Signup → 2. Personal Info → 3. Personality Test →
4. Browse Caregivers → 5. Request Matching → 6. Confirm → Done

CAREGIVER FIRST-TIME FLOW:
1. Signup → 2. Professional Info → 3. Care Style Test →
4. Upload Certifications → 5. Set Availability → Done

DAILY CAREGIVER WORKFLOW:
1. Open app → 2. View today's schedule → 3. Start care session →
4. End session → 5. Submit daily report → 6. Confirm

FAMILY MONITORING WORKFLOW:
1. Open dashboard → 2. View patient status → 3. Read latest report →
4. Check satisfaction trends → 5. Communicate if needed

DESIGN CONSISTENCY:
- Consistent color coding (Status, importance levels)
- Standard icons for common actions
- Consistent button styles and states
- Standard spacing and layout grids
- Unified typography scale
```

---

## 사용 방법

위 프롬프트 중 필요한 것을 선택해서 Google Stitch (또는 유사한 AI UI 도구)에 복사-붙여넣기 하면 됩니다.

### 추천 순서:
1. **프롬프트 1** → 전체 구조 이해
2. **프롬프트 8** → 네비게이션 구조
3. **프롬프트 2** → 성향 테스트 UI
4. **프롬프트 3** → 매칭 결과
5. **프롬프트 4** → 상세 프로필
6. **프롬프트 5** → 환자 대시보드
7. **프롬프트 6** → 간병인 리포트
8. **프롬프트 7** → 관리자 대시보드

### 커스터마이징 팁:
- 색상, 폰트, 로고 등은 별도로 지정
- 특정 언어 (한국어/영어) 선택
- 디자인 시스템 (Material Design, iOS, Custom) 지정
- 애니메이션 스타일 명시
