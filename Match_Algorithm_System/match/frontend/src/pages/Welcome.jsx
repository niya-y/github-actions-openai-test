function Welcome({ onNavigate }) {
  return (
    <div className="relative flex min-h-screen w-full flex-col font-display group/design-root" style={{minHeight: "100vh"}}>
      <div className="flex flex-col flex-1 justify-between">
        {/* Main Content */}
        <main className="flex flex-col flex-1">
          {/* Hero Image */}
          <div
            className="w-full flex flex-col justify-end overflow-hidden bg-center bg-no-repeat bg-cover min-h-[320px] sm:min-h-[400px]"
            style={{
              backgroundImage: 'url("https://lh3.googleusercontent.com/aida-public/AB6AXuCPNuAVLcNn9ok8nOVug0_k7aenrGChqr0e9FuIoJdfb9F7Vy748uVziGt-Lmi1fa-D1SwjfLPF5oaD3QUDzSg7gorVFX01DfgT0GgOOEDP7mhdvAcWGJPrRhOLpeZQZnFtx07IIjTS1F1bKwrsYZFuxmSsMROeJyLfopDIJ9pxuLmpX_x35cMVvClc7M85v23ugizdoKl0TNBU98TOkYOQ6Iai9h-eL1OWBxDWVLiJmLrgEvxWuTfx_4BFmoytMKY2VE-oceNujKzw")'
            }}
          ></div>

          {/* Hero Text */}
          <div className="px-4 py-3 text-center">
            <h1 className="text-text-primary-light dark:text-text-primary-dark tracking-light text-[32px] font-bold leading-tight pb-3 pt-6">
              Find the Perfect Care Match
            </h1>
            <p className="text-text-secondary-light dark:text-text-secondary-dark text-base font-normal leading-normal pb-3 pt-1">
              Our AI-powered platform matches patients with the right caregivers based on personality, skills, and specific medical needs.
            </p>
          </div>
        </main>

        {/* Footer */}
        <footer className="p-4 pb-8">
          <div className="flex px-4 py-3">
            <button
              onClick={() => onNavigate('test')}
              className="flex min-w-[84px] max-w-[480px] cursor-pointer items-center justify-center overflow-hidden rounded-lg h-12 px-5 flex-1 bg-primary text-white text-base font-bold leading-normal tracking-[0.015em] hover:opacity-90 transition-opacity"
            >
              <span className="truncate">Get Started</span>
            </button>
          </div>
          <p
            className="text-text-secondary-light dark:text-text-secondary-dark text-sm font-normal leading-normal pb-3 pt-1 text-center underline cursor-pointer"
            onClick={() => alert('Sign In 기능은 준비 중입니다')}
          >
            Already have an account? Sign In
          </p>
        </footer>
      </div>
    </div>
  );
}

export default Welcome;
