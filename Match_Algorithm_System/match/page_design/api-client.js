/**
 * BluedonuLab API Client
 * REST API와 통신하는 간단한 클라이언트 라이브러리
 */

class BluedonuLabAPI {
  constructor(baseURL = "http://localhost:8000") {
    this.baseURL = baseURL;
    this.headers = {
      "Content-Type": "application/json",
    };
  }

  /**
   * GET 요청
   */
  async get(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: "GET",
        headers: this.headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ GET ${endpoint} 실패:`, error);
      throw error;
    }
  }

  /**
   * POST 요청
   */
  async post(endpoint, data) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: "POST",
        headers: this.headers,
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ POST ${endpoint} 실패:`, error);
      throw error;
    }
  }

  /**
   * DELETE 요청
   */
  async delete(endpoint) {
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        method: "DELETE",
        headers: this.headers,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`❌ DELETE ${endpoint} 실패:`, error);
      throw error;
    }
  }

  // ====================================================================
  // 성향 API
  // ====================================================================

  /**
   * 환자의 성향 테스트 결과 저장
   * @param {number} patientId - 환자 ID
   * @param {number[]} testAnswers - 12개 질문 답변 (0-2)
   */
  async savePersonalityTest(patientId, testAnswers) {
    console.log(`🔄 환자 ${patientId} 성향 저장 중...`);
    return this.post("/api/personality/test", {
      patient_id: patientId,
      test_answers: testAnswers,
    });
  }

  /**
   * 환자의 성향 정보 조회
   * @param {number} patientId - 환자 ID
   */
  async getPersonality(patientId) {
    console.log(`🔄 환자 ${patientId} 성향 조회 중...`);
    return this.get(`/api/personality/${patientId}`);
  }

  /**
   * 모든 환자의 성향 목록 조회
   * @param {number} limit - 조회 개수
   * @param {number} offset - 시작 위치
   */
  async listPersonalities(limit = 100, offset = 0) {
    console.log(`🔄 성향 목록 조회 (limit: ${limit}, offset: ${offset})...`);
    return this.get(
      `/api/personality/list/all?limit=${limit}&offset=${offset}`
    );
  }

  /**
   * 성향 통계 조회
   */
  async getPersonalityStats() {
    console.log(`🔄 성향 통계 조회 중...`);
    return this.get("/api/personality/stats/summary");
  }

  // ====================================================================
  // 매칭 API
  // ====================================================================

  /**
   * 환자에게 추천할 간병인 목록 조회
   * @param {number} patientId - 환자 ID
   * @param {number} limit - 추천 개수
   */
  async recommendCaregivers(patientId, limit = 5) {
    console.log(`🔄 환자 ${patientId}에게 간병인 ${limit}명 추천 중...`);
    return this.get(
      `/api/matching/recommend/${patientId}?limit=${limit}`
    );
  }

  /**
   * 매칭 생성
   * @param {number} patientId - 환자 ID
   * @param {number} caregiverId - 간병인 ID
   */
  async createMatching(patientId, caregiverId) {
    console.log(
      `🔄 환자 ${patientId}와 간병인 ${caregiverId} 매칭 생성 중...`
    );
    return this.post("/api/matching/create", {
      patient_id: patientId,
      caregiver_id: caregiverId,
    });
  }

  /**
   * 환자의 매칭 이력 조회
   * @param {number} patientId - 환자 ID
   */
  async getMatchingHistory(patientId) {
    console.log(`🔄 환자 ${patientId} 매칭 이력 조회 중...`);
    return this.get(`/api/matching/history/${patientId}`);
  }

  /**
   * 매칭 취소
   * @param {number} matchingId - 매칭 ID
   * @param {string} reason - 취소 사유
   */
  async cancelMatching(matchingId, reason = "사용자 요청") {
    console.log(`🔄 매칭 ${matchingId} 취소 중...`);
    return this.delete(
      `/api/matching/${matchingId}?reason=${encodeURIComponent(reason)}`
    );
  }

  /**
   * 매칭 성능 평가
   * @param {string} startDate - 시작 날짜 (YYYY-MM-DD)
   * @param {string} endDate - 종료 날짜 (YYYY-MM-DD)
   */
  async getMatchingPerformance(startDate, endDate) {
    console.log(
      `🔄 매칭 성능 평가 조회 (${startDate} ~ ${endDate})...`
    );
    return this.get(
      `/api/matching/performance/evaluate?start_date=${startDate}&end_date=${endDate}`
    );
  }

  // ====================================================================
  // 리포트 API
  // ====================================================================

  /**
   * 일일 리포트 생성
   * @param {object} reportData - 리포트 데이터
   */
  async generateDailyReport(reportData) {
    console.log(`🔄 일일 리포트 생성 중...`);
    return this.post("/api/report/daily", reportData);
  }

  /**
   * 주간 리포트 조회
   * @param {number} patientId - 환자 ID
   * @param {string} weekStartDate - 주간 시작 날짜 (YYYY-MM-DD)
   */
  async getWeeklyReport(patientId, weekStartDate = null) {
    console.log(`🔄 환자 ${patientId} 주간 리포트 조회 중...`);
    if (weekStartDate) {
      return this.get(
        `/api/report/weekly/${patientId}?week_start_date=${weekStartDate}`
      );
    }
    return this.get(`/api/report/weekly/${patientId}`);
  }

  /**
   * 월간 성과 리포트 조회
   * @param {string} startDate - 시작 날짜 (YYYY-MM-DD)
   * @param {string} endDate - 종료 날짜 (YYYY-MM-DD)
   */
  async getMonthlyReport(startDate, endDate) {
    console.log(
      `🔄 월간 성과 리포트 조회 (${startDate} ~ ${endDate})...`
    );
    return this.get(
      `/api/report/monthly/performance?start_date=${startDate}&end_date=${endDate}`
    );
  }

  // ====================================================================
  // 헬스 체크
  // ====================================================================

  /**
   * API 서버 상태 확인
   */
  async healthCheck() {
    console.log(`🔄 API 서버 상태 확인 중...`);
    return this.get("/health");
  }

  /**
   * API 상태 조회
   */
  async getAPIStatus() {
    console.log(`🔄 API 상태 조회 중...`);
    return this.get("/api/status");
  }
}

// 전역 API 클라이언트 인스턴스 생성
const api = new BluedonuLabAPI();

console.log("✅ BluedonuLab API 클라이언트 로드됨");
