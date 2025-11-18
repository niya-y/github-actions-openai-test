import { useState, useEffect } from 'react';

function Dashboard() {
  const [matchings, setMatchings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadMatchingHistory();
  }, []);

  const loadMatchingHistory = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/matching/history/1');
      if (!response.ok) throw new Error('Failed to load matching history');
      const data = await response.json();
      setMatchings(data.matchings || []);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error loading matchings:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelMatching = async (matchingId) => {
    if (!window.confirm('이 매칭을 취소하시겠습니까?')) return;

    try {
      const response = await fetch(`http://localhost:8000/api/matching/${matchingId}`, {
        method: 'DELETE',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason: '사용자 요청' })
      });

      if (!response.ok) throw new Error('Failed to cancel matching');

      alert('매칭이 취소되었습니다.');
      loadMatchingHistory();
    } catch (error) {
      alert(`❌ 취소 실패: ${error.message}`);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-2">매칭 현황</h2>
      <p className="text-gray-600 mb-8">진행 중인 매칭과 매칭 이력</p>

      {loading && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">데이터를 불러오는 중...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-300 text-red-700 p-4 rounded-lg mb-8">
          오류: {error}
        </div>
      )}

      {!loading && !error && matchings.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">현재 진행 중인 매칭이 없습니다</p>
          <p className="text-gray-500 mt-2">성향 테스트를 통해 간병인을 추천받으세요</p>
        </div>
      )}

      {!loading && !error && matchings.length > 0 && (
        <div>
          {/* Active Matchings */}
          <div className="mb-12">
            <h3 className="text-2xl font-bold mb-6">🟢 활성 매칭</h3>
            <div className="space-y-4">
              {matchings
                .filter(m => m.status === 'Active')
                .map((matching) => (
                  <div key={matching.matching_id} className="border-2 border-green-300 bg-green-50 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h4 className="text-2xl font-bold">{matching.caregiver_name}</h4>
                        <p className="text-gray-600 mt-1">
                          시작: {new Date(matching.started_at).toLocaleDateString('ko-KR')}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-4xl font-bold text-blue-600">{matching.matching_score.toFixed(1)}</div>
                        <span className="inline-block px-3 py-1 bg-green-200 text-green-800 rounded text-sm font-bold mt-2">
                          {matching.status}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => handleCancelMatching(matching.matching_id)}
                      className="w-full bg-red-600 text-white py-2 rounded font-bold hover:bg-red-700 transition"
                    >
                      매칭 취소
                    </button>
                  </div>
                ))}
            </div>
          </div>

          {/* Past Matchings */}
          {matchings.filter(m => m.status !== 'Active').length > 0 && (
            <div>
              <h3 className="text-2xl font-bold mb-6">📋 과거 매칭</h3>
              <div className="space-y-4">
                {matchings
                  .filter(m => m.status !== 'Active')
                  .map((matching) => (
                    <div key={matching.matching_id} className="border-2 border-gray-300 rounded-lg p-6">
                      <div className="flex justify-between items-start">
                        <div>
                          <h4 className="text-xl font-bold">{matching.caregiver_name}</h4>
                          <p className="text-gray-600 mt-1">
                            기간: {new Date(matching.started_at).toLocaleDateString('ko-KR')} ~{' '}
                            {matching.ended_at ? new Date(matching.ended_at).toLocaleDateString('ko-KR') : '진행 중'}
                          </p>
                        </div>
                        <div className="text-right">
                          <div className="text-2xl font-bold text-gray-600">{matching.matching_score.toFixed(1)}</div>
                          <span className="inline-block px-3 py-1 bg-gray-200 text-gray-800 rounded text-sm font-bold mt-2">
                            {matching.status}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default Dashboard;
