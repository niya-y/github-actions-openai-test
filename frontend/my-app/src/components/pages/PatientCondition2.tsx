"use client"

import { useState } from 'react'
import { background, firstPrimary, secondPrimary } from '@/app/colors'

interface PatientCondition2Props {
  onNext: () => void
  onPrev: () => void
  initialData?: any
  onDataChange?: (data: any) => void
}

export default function PatientCondition2({ onNext, onPrev, initialData = {}, onDataChange }: PatientCondition2Props) {
  const [selectedDiseases, setSelectedDiseases] = useState<string[]>(initialData.selectedDiseases || ['dementia', 'diabetes', 'hypertension'])
  const [selectedMobility, setSelectedMobility] = useState(initialData.selectedMobility || 'assistive-device')
  const [otherDisease, setOtherDisease] = useState(initialData.otherDisease || '')

  const diseases = [
    { id: 'dementia', icon: '🧠', name: '치매/인지장애' },
    { id: 'stroke', icon: '⚡', name: '뇌졸중/중풍' },
    { id: 'cancer', icon: '🎗️', name: '암' },
    { id: 'diabetes', icon: '🍬', name: '당뇨병' },
    { id: 'hypertension', icon: '❤️', name: '고혈압' },
    { id: 'parkinsons', icon: '🤝', name: '파킨슨병' },
    { id: 'arthritis', icon: '🦴', name: '관절염' },
    { id: 'other', icon: '➕', name: '기타' }
  ]

  const mobilityOptions = [
    { id: 'independent', icon: '🚶', label: '혼자 걸을 수 있음', desc: '보조 없이 독립 보행 가능' },
    { id: 'assistive-device', icon: '🦯', label: '보조 기구 필요', desc: '지팡이, 워커 등 사용' },
    { id: 'wheelchair', icon: '♿', label: '휠체어 사용', desc: '휠체어로 이동' },
    { id: 'bedridden', icon: '🛏️', label: '침상 생활', desc: '거동 불가, 침대에서만 생활' }
  ]

  const toggleDisease = (id: string) => {
    const updated = selectedDiseases.includes(id)
      ? selectedDiseases.filter(d => d !== id)
      : [...selectedDiseases, id]
    setSelectedDiseases(updated)
    onDataChange?.({ selectedDiseases: updated, selectedMobility, otherDisease })
  }

  const handleMobilityChange = (id: string) => {
    setSelectedMobility(id)
    onDataChange?.({ selectedDiseases, selectedMobility: id, otherDisease })
  }

  const handleOtherDiseaseChange = (value: string) => {
    setOtherDisease(value)
    onDataChange?.({ selectedDiseases, selectedMobility, otherDisease: value })
  }

  const styles = {
    container: {
      width: '100%',
      background: background,
      display: 'flex',
      flexDirection: 'column' as const,
      minHeight: 'calc(100vh - 64px - 80px)',
      paddingBottom: '100px'
    },
    navBar: {
      display: 'flex',
      alignItems: 'center',
      padding: '15px 20px',
      borderBottom: '1px solid #f0f0f0'
    },
    backBtn: {
      fontSize: '20px',
      cursor: 'pointer',
      color: firstPrimary,
      background: 'none',
      border: 'none'
    },
    progress: {
      flex: 1,
      margin: '0 20px'
    },
    progressBar: {
      width: '100%',
      height: '4px',
      background: '#f0f0f0',
      borderRadius: '2px',
      overflow: 'hidden'
    },
    progressFill: {
      height: '100%',
      background: firstPrimary,
      width: '40%',
      borderRadius: '2px'
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '30px 20px'
    },
    headerText: {
      marginBottom: '30px'
    },
    h2: {
      fontSize: '26px',
      color: '#333',
      marginBottom: '8px'
    },
    p: {
      fontSize: '14px',
      color: '#666'
    },
    section: {
      marginBottom: '35px'
    },
    sectionTitle: {
      fontSize: '16px',
      fontWeight: 600,
      color: '#333',
      marginBottom: '12px'
    },
    sectionSubtitle: {
      fontSize: '13px',
      color: '#666',
      marginBottom: '15px'
    },
    diseaseGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(2, 1fr)',
      gap: '10px'
    },
    diseaseCard: {
      padding: '15px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      textAlign: 'center' as const,
      cursor: 'pointer',
      transition: 'all 0.2s'
    },
    diseaseCardSelected: {
      borderColor: firstPrimary,
      background: '#f0f4ff'
    },
    diseaseIcon: {
      fontSize: '32px',
      marginBottom: '8px'
    },
    diseaseName: {
      fontSize: '14px',
      color: '#333',
      fontWeight: 500
    },
    otherInput: {
      marginTop: '10px'
    },
    input: {
      width: '100%',
      padding: '12px',
      border: '1px solid #e0e0e0',
      borderRadius: '8px',
      fontSize: '14px',
      boxSizing: 'border-box' as const
    },
    mobilityOptions: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '12px'
    },
    mobilityOption: {
      padding: '15px',
      border: '2px solid #e0e0e0',
      borderRadius: '12px',
      cursor: 'pointer',
      transition: 'all 0.2s',
      display: 'flex',
      alignItems: 'center',
      gap: '12px'
    },
    mobilityOptionSelected: {
      borderColor: firstPrimary,
      background: '#f0f4ff'
    },
    mobilityIcon: {
      fontSize: '24px',
      minWidth: '30px'
    },
    mobilityText: {
      flex: 1
    },
    mobilityLabel: {
      fontSize: '15px',
      fontWeight: 600,
      color: '#333',
      marginBottom: '3px'
    },
    mobilityDesc: {
      fontSize: '12px',
      color: '#666'
    },
    bottomBar: {
      padding: '20px',
      background: background,
      borderTop: '1px solid #f0f0f0',
      display: 'flex',
      gap: '10px'
    },
    button: {
      flex: 1,
      padding: '18px',
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      fontSize: '17px',
      fontWeight: 600,
      cursor: 'pointer'
    },
    prevButton: {
      background: '#e0e0e0',
      color: '#333'
    },
    nextButton: {
      background: firstPrimary
    }
  }

  return (
    <div style={styles.container}>
      <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={onPrev}>‹</button>
        <div style={styles.progress}>
          <div style={styles.progressBar}>
            <div style={styles.progressFill}></div>
          </div>
        </div>
        <div style={{width: '60px'}}></div>
      </div>

      <div style={styles.content}>
        <div style={styles.headerText}>
          <h2 style={styles.h2}>건강 상태를 알려주세요</h2>
          <p style={styles.p}>더 정확한 간병 계획을 위해 필요합니다</p>
        </div>

        <div style={styles.section}>
          <div style={styles.sectionTitle}>주요 질병을 선택해주세요</div>
          <div style={styles.sectionSubtitle}>중복 선택 가능</div>

          <div style={styles.diseaseGrid}>
            {diseases.map(disease => (
              <div
                key={disease.id}
                style={{
                  ...styles.diseaseCard,
                  ...(selectedDiseases.includes(disease.id) ? styles.diseaseCardSelected : {})
                }}
                onClick={() => toggleDisease(disease.id)}
              >
                <div style={styles.diseaseIcon}>{disease.icon}</div>
                <div style={styles.diseaseName}>{disease.name}</div>
              </div>
            ))}
          </div>

          {selectedDiseases.includes('other') && (
            <div style={styles.otherInput}>
              <input
                type="text"
                style={styles.input}
                placeholder="기타 질병명을 입력하세요"
                value={otherDisease}
                onChange={(e) => handleOtherDiseaseChange(e.target.value)}
              />
            </div>
          )}
        </div>

        <div style={styles.section}>
          <div style={styles.sectionTitle}>스스로 움직이실 수 있나요?</div>

          <div style={styles.mobilityOptions}>
            {mobilityOptions.map(option => (
              <div
                key={option.id}
                style={{
                  ...styles.mobilityOption,
                  ...(selectedMobility === option.id ? styles.mobilityOptionSelected : {})
                }}
                onClick={() => handleMobilityChange(option.id)}
              >
                <div style={styles.mobilityIcon}>{option.icon}</div>
                <div style={styles.mobilityText}>
                  <div style={styles.mobilityLabel}>{option.label}</div>
                  <div style={styles.mobilityDesc}>{option.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div style={styles.bottomBar}>
        <button style={{...styles.button, ...styles.prevButton}} onClick={onPrev}>이전</button>
        <button style={{...styles.button, ...styles.nextButton}} onClick={onNext}>다음</button>
      </div>
    </div>
  )
}
