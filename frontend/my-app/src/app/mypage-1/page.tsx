'use client';

import Image from 'next/image';
import Link from 'next/link';
import { background, firstPrimary, secondPrimary } from '../colors'

export default function CaregiverProfile() {
  return (
      <div className="min-h-screen flex flex-col items-center p-6" style={{ minHeight: 'max(884px, 100dvh)' }}>
        <div className="w-full max-w-sm mx-auto text-center flex flex-col pt-12">
          <div>
            <div className="mb-8">
              <p className="text-lg text-gray-600 dark:text-gray-400 mb-2">매칭되었습니다</p>
              <h1 className="text-3xl font-bold text-gray-800 dark:text-gray-100">김미숙</h1>
            </div>

            <div className="relative flex justify-center items-center mb-6">
            <svg className="absolute w-64 h-64" viewBox="0 0 120 120">
              <circle
                className="text-gray-100 dark:text-gray-800"
                cx="60"
                cy="60"
                fill="transparent"
                r="54"
                stroke="currentColor"
                strokeWidth="6"
              />
              <circle
                className="progress-ring__circle text-teal-400"
                cx="60"
                cy="60"
                fill="transparent"
                r="54"
                stroke="currentColor"
                strokeLinecap="round"
                strokeWidth="6"
                style={{ strokeDasharray: '339.292', strokeDashoffset: '84.823' }}
              />
            </svg>
            <div className="w-48 h-48 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center overflow-hidden">
              {/* <Image
                alt="Profile picture of caregiver Kim Misuk"
                className="w-full h-full object-cover"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuDG5402m5QvlOGTA24iWbO3EkYVKqPrMc_6pVF4ASlOzTt3vix_3LejI54vcrmbsVzGRGAs_yOGlWdUl6urV702TaIYpf4_p6BilnIPVVFVDS5Ei9pHjPGaAzUfKpbyxmy7e7BjnjNTsh7NtAzNcMd8BnlMGb5GpXA_fNcx-Qrt2E1w9TevFjQqJwWGA7tbqw_tuPawMBgY9KKrcYE70dav2BQWg1Q-c0_cAPqvKPL0PTryAl63SB-rb0I9ry-9PwDO9AwXmsKlPPyu"
                width={192}
                height={192}
              /> */}
            </div>
            </div>
          </div>

          <div className="space-y-4 mt-8">
            <Link href="/care-plans-create-1" className="w-full border border-gray-100 dark:border-gray-700 rounded-xl p-4 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow" style={{ backgroundColor: firstPrimary }}>
              <span className="text-lg font-medium text-white">AI 간병 일정 만들기</span>
            </Link>

            <button className="w-full border border-gray-100 dark:border-gray-700 rounded-xl p-4 flex items-center justify-center shadow-sm hover:shadow-md transition-shadow" style={{ backgroundColor: firstPrimary }}>
              <span className="text-lg font-medium text-white">채팅하기</span>
            </button>
          </div>
        </div>
      </div>
  );
}
