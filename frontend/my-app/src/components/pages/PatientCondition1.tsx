'use client'

import { useState } from 'react'
import { background, firstPrimary, secondPrimary } from '@/app/colors'

interface PatientCondition1Props {
  onNext: () => void
  initialData?: any
  onDataChange?: (data: any) => void
}

export default function PatientCondition1({ onNext, initialData = {}, onDataChange }: PatientCondition1Props) {
  const [formData, setFormData] = useState({
    name: initialData.name || '',
    birthDate: initialData.birthDate || '',
    gender: initialData.gender || 'female',
    relationship: initialData.relationship || '',
    isDirectInput: false
  })

  const handleChange = (newData: any) => {
    const updated = { ...formData, ...newData }
    setFormData(updated)
    onDataChange?.(updated)
  }

  const toggleDirectInput = () => {
    handleChange({ isDirectInput: !formData.isDirectInput, relationship: '' })
  }

  const styles = {
    container: {
      background: background,
      display: 'flex',
      flexDirection: 'column' as const,
      minHeight: 'calc(100vh - 64px - 80px)',
      paddingBottom: '100px'
    },
    // Status bar removed
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
      width: '20%',
      borderRadius: '2px'
    },
    content: {
      flex: 1,
      overflowY: 'auto' as const,
      padding: '30px 20px'
    },
    headerText: {
      marginBottom: '40px'
    },
    h2: {
      fontSize: '28px',
      color: '#000',
      marginBottom: '10px'
    },
    p: {
      fontSize: '15px',
      color: '#000'
    },
    formGroup: {
      marginBottom: '20px'
    },
    formLabel: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      fontSize: '14px',
      fontWeight: 600,
      color: '#000',
      marginBottom: '8px'
    },
    required: {
      color: secondPrimary
    },
    formInput: {
      width: '100%',
      padding: '15px',
      border: '1px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: '16px',
      fontFamily: 'inherit',
      boxSizing: 'border-box' as const,
      color: '#000'
    },
    radioGroup: {
      display: 'flex',
      gap: '10px'
    },
    radioOption: {
      flex: 1,
      padding: '15px',
      borderWidth: '2px',
      borderStyle: 'solid',
      borderColor: '#e0e0e0',
      borderRadius: '12px',
      textAlign: 'center' as const,
      cursor: 'pointer',
      transition: 'all 0.2s',
      color: '#000'
    },
    radioOptionSelected: {
      borderWidth: '2px',
      borderStyle: 'solid',
      borderColor: firstPrimary,
      background: '#f0f4ff'
    },
    selectWrapper: {
      position: 'relative' as const
    },
    select: {
      width: '100%',
      padding: '15px',
      border: '1px solid #e0e0e0',
      borderRadius: '12px',
      fontSize: '16px',
      fontFamily: 'inherit',
      appearance: 'none' as const,
      background: 'white',
      boxSizing: 'border-box' as const,
      color: '#000'
    },
    bottomBar: {
      padding: '20px',
      background: background,
      borderTop: '1px solid #f0f0f0'
    },
    nextButton: {
      width: '100%',
      padding: '18px',
      background: firstPrimary,
      color: 'white',
      border: 'none',
      borderRadius: '12px',
      fontSize: '17px',
      fontWeight: 600,
      cursor: 'pointer'
    },
    toggleSwitch: {
      position: 'relative' as const,
      width: '40px',
      height: '24px',
      background: formData.isDirectInput ? firstPrimary : '#ccc',
      borderRadius: '12px',
      cursor: 'pointer',
      transition: 'background 0.3s'
    },
    toggleKnob: {
      position: 'absolute' as const,
      top: '2px',
      left: formData.isDirectInput ? '18px' : '2px',
      width: '20px',
      height: '20px',
      background: 'white',
      borderRadius: '50%',
      transition: 'left 0.3s',
      boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
    }
  }

  return (
    <div style={styles.container}>
      {/* Status bar removed */}

      <div style={styles.navBar}>
        <button style={styles.backBtn} onClick={() => { }}>‹</button>
        <div style={styles.progress}>
          <div style={styles.progressBar}>
            <div style={styles.progressFill}></div>
          </div>
        </div>
        <div style={{ fontSize: '14px', color: '#000', cursor: 'pointer' }}>건너뛰기</div>
      </div>

      <div style={styles.content}>
        <div style={styles.headerText}>
          <h2 style={styles.h2}>도움이 필요해요</h2>
          <p style={styles.p}>케어 대상자의 기본 정보를 입력해주세요</p>
        </div>

        <form>
          <div style={styles.formGroup}>
            <label style={styles.formLabel}>
              <span>이름 <span style={styles.required}>*</span></span>
            </label>
            <input
              type="text"
              style={styles.formInput}
              placeholder="예: 김영희"
              value={formData.name}
              onChange={(e) => handleChange({ name: e.target.value })}
              required
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.formLabel}>
              <span>생년월일 <span style={styles.required}>*</span></span>
            </label>
            <input
              type="date"
              style={styles.formInput}
              value={formData.birthDate}
              onChange={(e) => handleChange({ birthDate: e.target.value })}
              required
            />
          </div>

          <div style={styles.formGroup}>
            <label style={styles.formLabel}>
              <span>성별 <span style={styles.required}>*</span></span>
            </label>
            <div style={styles.radioGroup}>
              <div
                style={{ ...styles.radioOption, ...(formData.gender === 'female' ? styles.radioOptionSelected : {}) }}
                onClick={() => handleChange({ gender: 'female' })}
              >
                여성
              </div>
              <div
                style={{ ...styles.radioOption, ...(formData.gender === 'male' ? styles.radioOptionSelected : {}) }}
                onClick={() => handleChange({ gender: 'male' })}
              >
                남성
              </div>
            </div>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.formLabel}>
              <span>보호자와 관계 <span style={styles.required}>*</span></span>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '12px', fontWeight: 'normal', color: '#666' }}>직접 입력</span>
                <div style={styles.toggleSwitch} onClick={toggleDirectInput}>
                  <div style={styles.toggleKnob}></div>
                </div>
              </div>
            </label>
            <div style={styles.selectWrapper}>
              {formData.isDirectInput ? (
                <input
                  type="text"
                  style={styles.formInput}
                  placeholder="관계를 입력해주세요"
                  value={formData.relationship}
                  onChange={(e) => handleChange({ relationship: e.target.value })}
                  required
                />
              ) : (
                <select
                  style={styles.select}
                  value={formData.relationship}
                  onChange={(e) => handleChange({ relationship: e.target.value })}
                  required
                >
                  <option value="">선택해주세요</option>
                  <option value="어머니">어머니</option>
                  <option value="아버지">아버지</option>
                  <option value="배우자">배우자</option>
                  <option value="조부모">조부모</option>
                  <option value="기타">기타</option>
                </select>
              )}
            </div>
          </div>
        </form>
      </div>

      <div style={styles.bottomBar}>
        <button style={styles.nextButton} onClick={onNext}>다음</button>
      </div>
    </div>
  )
}
