import { useState } from 'react';

const QUESTIONS = [
  { question: "혼자 있을 때 편안함을 느끼시나요?", options: ["매우 그렇다", "보통이다", "그렇지 않다"] },
  { question: "새로운 사람을 만나는 것을 좋아하시나요?", options: ["매우 좋아한다", "보통이다", "좋아하지 않는다"] },
  { question: "정해진 일정대로 생활하는 것을 선호하시나요?", options: ["매우 선호한다", "보통이다", "선호하지 않는다"] },
  { question: "타인의 감정을 잘 이해하는 편인가요?", options: ["매우 그렇다", "보통이다", "그렇지 않다"] },
  { question: "활동적인 취미를 즐기시나요?", options: ["매우 즐긴다", "보통이다", "즐기지 않는다"] },
  { question: "인내심이 있는 편인가요?", options: ["매우 그렇다", "보통이다", "그렇지 않다"] },
  { question: "혼자 결정하는 것을 선호하시나요?", options: ["매우 선호한다", "보통이다", "선호하지 않는다"] },
  { question: "다른 사람의 도움을 쉽게 받아들이시나요?", options: ["매우 그렇다", "보통이다", "그렇지 않다"] },
  { question: "규칙을 중요하게 생각하시나요?", options: ["매우 중요하다", "보통이다", "중요하지 않다"] },
  { question: "변화에 잘 적응하시나요?", options: ["매우 잘한다", "보통이다", "잘하지 못한다"] },
  { question: "조용한 환경을 선호하시나요?", options: ["매우 선호한다", "보통이다", "선호하지 않는다"] },
  { question: "타인과의 상호작용을 즐기시나요?", options: ["매우 즐긴다", "보통이다", "즐기지 않는다"] }
];

function PersonalityTest({ onNavigate }) {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [completed, setCompleted] = useState(false);

  const handleAnswer = (answerIndex) => {
    const newAnswers = [...answers];
    newAnswers[currentQuestion] = answerIndex;
    setAnswers(newAnswers);
  };

  const handleSubmit = async () => {
    if (answers.length < QUESTIONS.length) {
      alert('모든 질문에 답변해주세요');
      return;
    }

    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/personality/test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: 1,
          test_answers: answers
        })
      });

      if (!response.ok) throw new Error('Test submission failed');

      setCompleted(true);
    } catch (error) {
      alert('테스트 제출 실패: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  const currentQ = QUESTIONS[currentQuestion];
  const progress = ((currentQuestion + 1) / QUESTIONS.length) * 100;

  if (completed) {
    return (
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-2xl mx-auto">
        <div className="text-center py-12">
          <div className="text-6xl mb-4">✅</div>
          <h2 className="text-3xl font-bold mb-4 text-green-600">테스트 완료!</h2>
          <p className="text-gray-600 mb-8 text-lg">
            당신의 성향 프로필이 저장되었습니다.
            이제 맞춤 간병인을 추천받을 수 있습니다!
          </p>
          <button
            onClick={() => onNavigate('recommendations')}
            className="bg-blue-600 text-white px-8 py-3 rounded-lg font-bold hover:bg-blue-700 text-lg"
          >
            간병인 추천 보기 →
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white p-8 rounded-lg shadow-lg max-w-2xl mx-auto">
      <h2 className="text-3xl font-bold mb-2">성향 테스트</h2>
      <p className="text-gray-600 mb-8">당신의 성향을 파악하여 최적의 간병인을 찾아드립니다</p>

      {/* Progress Bar */}
      <div className="mb-8">
        <div className="flex justify-between mb-2">
          <span className="font-bold">질문 {currentQuestion + 1}/{QUESTIONS.length}</span>
          <span className="text-gray-600">{Math.round(progress)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div className="bg-blue-600 h-2 rounded-full transition-all" style={{ width: `${progress}%` }}></div>
        </div>
      </div>

      {/* Question */}
      <div className="mb-8">
        <h3 className="text-2xl font-bold mb-6">{currentQ.question}</h3>
        <div className="space-y-3">
          {currentQ.options.map((option, idx) => (
            <label
              key={idx}
              className={`flex items-center p-4 border-2 rounded-lg cursor-pointer transition ${
                answers[currentQuestion] === idx
                  ? 'border-blue-600 bg-blue-50'
                  : 'border-gray-200 hover:border-blue-400'
              }`}
            >
              <input
                type="radio"
                name="answer"
                checked={answers[currentQuestion] === idx}
                onChange={() => handleAnswer(idx)}
                className="mr-4 w-5 h-5"
              />
              <span className="text-lg">{option}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Navigation */}
      <div className="flex gap-4">
        <button
          onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
          disabled={currentQuestion === 0}
          className="px-6 py-2 border rounded font-bold hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          ← 이전
        </button>

        {currentQuestion < QUESTIONS.length - 1 ? (
          <button
            onClick={() => setCurrentQuestion(currentQuestion + 1)}
            disabled={answers[currentQuestion] === undefined}
            className="flex-1 px-6 py-2 bg-blue-600 text-white rounded font-bold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            다음 →
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={loading || answers.length < QUESTIONS.length}
            className="flex-1 px-6 py-2 bg-green-600 text-white rounded font-bold hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? '제출 중...' : '제출하기'}
          </button>
        )}
      </div>
    </div>
  );
}

export default PersonalityTest;
