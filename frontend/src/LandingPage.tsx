import { ArrowDown, ArrowRight, BookOpen, CalendarDays, MapPinned, Moon, Sun } from 'lucide-react';
import './landing.css';

export type Theme = 'light' | 'dark';

type ThemeToggleProps = {
  theme: Theme;
  onToggle: () => void;
};

export function ThemeToggle({ theme, onToggle }: ThemeToggleProps) {
  const isDark = theme === 'dark';
  return (
    <button className="theme-toggle" type="button" onClick={onToggle} aria-label={`Switch to ${isDark ? 'light' : 'dark'} theme`}>
      {isDark ? <Sun size={16} /> : <Moon size={16} />}
      <span>{isDark ? 'Light theme' : 'Dark theme'}</span>
    </button>
  );
}

type LandingPageProps = ThemeToggleProps & {
  onSignIn: () => void;
};

export default function LandingPage({ theme, onToggle, onSignIn }: LandingPageProps) {
  return (
    <main className="landing-page">
      <header className="landing-nav">
        <a className="landing-brand" href="#home" aria-label="DDUGU Smart Campus home">
          <span className="landing-brand-mark">D</span>
          <span><b>DDUGU</b><small>SMART CAMPUS</small></span>
        </a>
        <nav aria-label="Main navigation">
          <a href="#features">Platform</a>
          <a href="#campus-map">Campus map</a>
        </nav>
        <div className="landing-actions">
          <ThemeToggle theme={theme} onToggle={onToggle} />
          <button className="primary landing-signin" type="button" onClick={onSignIn}>Sign in <ArrowRight size={16} /></button>
        </div>
      </header>

      <section className="landing-hero" id="home">
        <div className="landing-copy">
          <span className="landing-kicker"><span className="landing-live-dot" /> ONE CONNECTED CAMPUS</span>
          <h1>Campus life,<br />made <em>clearer.</em></h1>
          <p>DDUGU Smart Campus brings schedules, room availability, campus updates and wayfinding into one simple place for students, faculty and administrators.</p>
          <div className="landing-hero-actions">
            <button className="primary" type="button" onClick={onSignIn}>Explore your campus <ArrowRight size={17} /></button>
            <a className="landing-text-link" href="#features">Discover the platform <ArrowDown size={15} /></a>
          </div>
          <small className="landing-demo-note">Demonstration prototype · sample records only</small>
        </div>
        <div className="landing-blueprint-card" id="campus-map">
          <div className="blueprint-card-head">
            <span><MapPinned size={15} /> CAMPUS BLUEPRINT</span>
            <span className="blueprint-status">IET · DEEKSHA BHAWAN</span>
          </div>
          <img src="/blueprints/campus-blueprint.png" alt="DDUGU IET and Deeksha Bhawan floor plan blueprint with labeled rooms" />
          <div className="blueprint-caption"><b>Two buildings. One connected campus.</b><span>Floor plan reference · verify locations on site</span></div>
        </div>
        <div className="landing-glow landing-glow-one" />
        <div className="landing-glow landing-glow-two" />
      </section>

      <section className="landing-features" id="features">
        <div className="landing-section-heading">
          <span className="landing-kicker">BUILT FOR CAMPUS LIFE</span>
          <h2>Less searching. More doing.</h2>
          <p>A shared view of the information people need to move through the university day.</p>
        </div>
        <div className="feature-grid">
          <article className="feature-card"><span className="feature-icon"><CalendarDays size={20} /></span><h3>Schedules in one view</h3><p>Check published timetables, exam details and campus announcements from a role-specific dashboard.</p></article>
          <article className="feature-card"><span className="feature-icon"><BookOpen size={20} /></span><h3>Smarter room coordination</h3><p>Find available rooms and submit classroom requests with clear review and approval steps.</p></article>
          <article className="feature-card"><span className="feature-icon"><MapPinned size={20} /></span><h3>Campus wayfinding</h3><p>Explore the supplied building blueprint and locate labeled blocks; verified routes require confirmed site data.</p></article>
        </div>
      </section>
      <footer className="landing-footer"><span>DDUGU SMART CAMPUS</span><span>Prototype for demonstration · Not an official university service</span></footer>
    </main>
  );
}
