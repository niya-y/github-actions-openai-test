import { useState, useEffect } from 'react';

function Recommendations({ onNavigate }) {
  const [caregivers, setCaregivers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadRecommendations();
  }, []);

  const loadRecommendations = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/api/matching/recommend/1?limit=10');
      if (!response.ok) throw new Error('Failed to load recommendations');
      const data = await response.json();
      setCaregivers(data.recommendations);
      setError(null);
    } catch (err) {
      setError(err.message);
      console.error('Error loading recommendations:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRequestMatching = async (caregiverId, caregiverName) => {
    try {
      const response = await fetch('http://localhost:8000/api/matching/create', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: 1,
          caregiver_id: caregiverId
        })
      });

      if (!response.ok) throw new Error('Matching request failed');

      alert(`✅ ${caregiverName}님과의 매칭 요청이 완료되었습니다!`);
      onNavigate('dashboard');
    } catch (error) {
      alert(`❌ 매칭 요청 실패: ${error.message}`);
    }
  };

  return (
    <div className="bg-white p-8 rounded-lg shadow-lg">
      <h2 className="text-3xl font-bold mb-2">맞춤 간병인 추천</h2>
      <p className="text-gray-600 mb-8">당신을 위해 엄선된 간병인들입니다</p>

      {loading && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">간병인을 불러오는 중...</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-300 text-red-700 p-4 rounded-lg mb-8">
          오류: {error}
        </div>
      )}

      {!loading && !error && caregivers.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">추천 간병인이 없습니다</p>
        </div>
      )}

      {!loading && !error && caregivers.length > 0 && (
        <div className="space-y-6">
          {caregivers.map((caregiver) => {
            const gradeColor = caregiver.grade === 'A'
              ? 'bg-green-100 text-green-800'
              : caregiver.grade === 'B'
              ? 'bg-blue-100 text-blue-800'
              : 'bg-yellow-100 text-yellow-800';

            return (
              <div key={caregiver.caregiver_id} className="border-2 border-gray-200 rounded-lg p-6 hover:shadow-lg transition">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-2xl font-bold">{caregiver.caregiver_name}</h3>
                    <p className="text-gray-600">{caregiver.job_title}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-4xl font-bold text-blue-600">{caregiver.matching_score.toFixed(1)}</div>
                    <span className={`inline-block px-4 py-1 rounded text-sm font-bold ${gradeColor}`}>
                      등급 {caregiver.grade}
                    </span>
                  </div>
                </div>

                {/* Match Details */}
                <div className="grid grid-cols-4 gap-4 mb-6 p-4 bg-gray-50 rounded">
                  <div>
                    <p className="text-sm text-gray-600">공감도</p>
                    <p className="text-2xl font-bold text-blue-600">{caregiver.empathy_match.toFixed(0)}점</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">의료기술</p>
                    <p className="text-2xl font-bold text-blue-600">{caregiver.care_compatibility.toFixed(0)}점</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">성격일치</p>
                    <p className="text-2xl font-bold text-blue-600">{caregiver.personality_compatibility.toFixed(0)}점</p>
                  </div>
                  <div>
                    <p className="text-sm text-gray-600">인내심</p>
                    <p className="text-2xl font-bold text-blue-600">{caregiver.patience_match.toFixed(0)}점</p>
                  </div>
                </div>

                {/* Recommendation Reason */}
                <div className="bg-blue-50 p-4 rounded mb-6 border-l-4 border-blue-600">
                  <p className="text-sm font-semibold text-blue-900 mb-2">추천 이유:</p>
                  <p className="text-gray-700">{caregiver.reason.substring(0, 200)}...</p>
                </div>

                {/* Action Button */}
                <button
                  onClick={() => handleRequestMatching(caregiver.caregiver_id, caregiver.caregiver_name)}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg font-bold hover:bg-blue-700 transition text-lg"
                >
                  매칭 요청하기
                </button>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default Recommendations;
