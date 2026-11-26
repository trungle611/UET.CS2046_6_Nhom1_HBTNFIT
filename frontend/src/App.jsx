import React, { useEffect, useState } from 'react';
import {
  Bell,
  CalendarDays,
  ChevronDown,
  CircleHelp,
  CircleUserRound,
  Dumbbell,
  House,
  LogOut,
  Menu,
  UtensilsCrossed,
} from 'lucide-react';
import GuidePanel from './GuidePanel.jsx';
import FoodHistory from './FoodHistory.jsx';
import AuthPage from './AuthPage.jsx';
import ScanHistory from './ScanHistory.jsx';
import ScanSection from './ScanSection.jsx';
import TodayMeals from './TodayMeals.jsx';
import WorkoutPlans from './WorkoutPlans.jsx';
import WorkoutPanel from './WorkoutPanel.jsx';
import ProfilePanel from './ProfilePanel.jsx';
import { apiCall, getAuthToken, saveAuthToken, clearAuthToken } from './api.js';

const navigation = [
  { id: 'home', label: 'Trang chủ', icon: House },
  { id: 'workout', label: 'Tập luyện', icon: Dumbbell },
  { id: 'food', label: 'Ăn uống', icon: UtensilsCrossed },
  { id: 'profile', label: 'Cá nhân', icon: CircleUserRound },
  { id: 'guide', label: 'Hướng dẫn', icon: CircleHelp },
];

function currentMealType() {
  const hour = new Date().getHours();
  if (hour >= 5 && hour < 10) return 'breakfast';
  if (hour >= 10 && hour < 14) return 'lunch';
  if (hour >= 17 && hour < 21) return 'dinner';
  return 'snack';
}

function Header({ user, onHome, onProfile, onLogout, navOpen, setNavOpen, loggingOut }) {
  const displayName = user.full_name || user.username || 'Tài khoản';
  const [showBell, setShowBell] = useState(false);
  const [showAccount, setShowAccount] = useState(false);

  function openProfile() {
    setShowAccount(false);
    onProfile();
  }

  function logout() {
    setShowAccount(false);
    onLogout();
  }

  return (
    <header className="topbar">
      <div className="topbar-inner">
        <button
          className="menu-toggle"
          aria-label="Mở điều hướng"
          aria-expanded={navOpen}
          onClick={() => setNavOpen(!navOpen)}
        >
          <Menu size={22} />
        </button>
        <button className="brand" onClick={onHome} aria-label="Về trang chủ HBTNFIT">
          <span className="brand-logo-frame">
            <img className="brand-logo" src="/Logo_HUET.svg" alt="Logo Đại học Công nghệ" />
          </span>
          <span className="brand-words">
            <span className="brand-name">HBTNFIT</span>
            <span className="brand-school">ĐẠI HỌC CÔNG NGHỆ</span>
          </span>
        </button>
        <span className="topbar-caption">Sống khỏe theo cách của bạn</span>
        <div className="top-actions">
          <div className="notification-wrap">
            <button
              className="header-icon"
              aria-label="Thông báo"
              aria-expanded={showBell}
              onClick={() => setShowBell(!showBell)}
            >
              <Bell size={19} />
            </button>
            {showBell && <div className="notification-popover">Chưa có thông báo mới.</div>}
          </div>
          <div className="account-wrap">
            <button
              className="account-button"
              aria-label="Mở menu tài khoản"
              aria-expanded={showAccount}
              onClick={() => setShowAccount(!showAccount)}
            >
              <span className="avatar">{displayName.slice(0, 1).toLocaleUpperCase('vi')}</span>
              <span>{displayName}</span>
              <ChevronDown size={15} />
            </button>
            {showAccount && (
              <div className="account-popover">
                <button onClick={openProfile}>
                  <CircleUserRound size={15} /> Trang cá nhân
                </button>
                <button disabled={loggingOut} onClick={logout}>
                  <LogOut size={15} /> {loggingOut ? 'Đang đăng xuất…' : 'Đăng xuất'}
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
}

function Sidebar({ section, navOpen, navigate }) {
  return (
    <aside className={`sidebar ${navOpen ? 'open' : ''}`}>
      <div className="sidebar-group">
        <span className="sidebar-label">ĐIỀU HƯỚNG</span>
        <nav aria-label="Điều hướng chính">
          {navigation.map((item) => {
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                className={`nav-item ${section === item.id ? 'active' : ''}`}
                onClick={() => navigate(item.id)}
                title={item.label}
                aria-current={section === item.id ? 'page' : undefined}
              >
                <Icon size={19} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </div>
      <div className="sidebar-bottom">
        <div className="sidebar-note">
          <span className="status-dot" /> Bản dùng thử Track 1
        </div>
        <small>HBTNFIT · 2026</small>
      </div>
    </aside>
  );
}

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(true);
  const [sessionError, setSessionError] = useState('');
  const [sessionVersion, setSessionVersion] = useState(0);
  const [loggingOut, setLoggingOut] = useState(false);

  useEffect(() => {
    let active = true;
    setChecking(true);
    setSessionError('');
    if (!getAuthToken()) {
      setChecking(false);
      return;
    }
    apiCall('/api/auth/me')
      .then((value) => {
        if (active) setUser(value);
      })
      .catch((error) => {
        if (active && error.status === 401) clearAuthToken();
        else if (active) setSessionError(error.message);
      })
      .finally(() => {
        if (active) setChecking(false);
      });
    return () => {
      active = false;
    };
  }, [sessionVersion]);

  useEffect(() => {
    const expired = () => setUser(null);
    const changed = (event) => {
      if (event.key === 'hbtnfit_auth_token') {
        setUser(null);
        setSessionVersion((value) => value + 1);
      }
    };
    window.addEventListener('hbtnfit-session-expired', expired);
    window.addEventListener('storage', changed);
    return () => {
      window.removeEventListener('hbtnfit-session-expired', expired);
      window.removeEventListener('storage', changed);
    };
  }, []);

  function authenticated(result) {
    saveAuthToken(result.access_token);
    setUser(result.user);
  }
  async function logout() {
    setLoggingOut(true);
    try {
      await apiCall('/api/auth/logout', { method: 'POST' });
      clearAuthToken();
      setUser(null);
    } catch (error) {
      if (error.status !== 401) window.alert(`${error.message} Chưa đăng xuất được; hãy thử lại.`);
    } finally {
      setLoggingOut(false);
    }
  }
  if (checking)
    return (
      <main className="auth-checking" role="status">
        Đang kiểm tra phiên đăng nhập…
      </main>
    );
  if (sessionError)
    return (
      <main className="auth-checking">
        <p role="alert">{sessionError}</p>
        <button className="secondary-button" onClick={() => setSessionVersion((v) => v + 1)}>
          Thử lại
        </button>
      </main>
    );
  if (!user) return <AuthPage onAuthenticated={authenticated} />;
  // Đổi tài khoản sẽ hủy toàn bộ state và ảnh của tài khoản trước.
  return <SignedInApp key={user.id} user={user} logout={logout} loggingOut={loggingOut} />;
}

function SignedInApp({ user, logout, loggingOut }) {
  const [section, setSection] = useState('home');
  const [navOpen, setNavOpen] = useState(false);
  const [foods, setFoods] = useState([]);
  const [dashboard, setDashboard] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loaded, setLoaded] = useState(false);
  const [notice, setNotice] = useState('');
  const [historyVersion, setHistoryVersion] = useState(0);
  const [selectedMeal, setSelectedMeal] = useState(currentMealType);
  const [plans, setPlans] = useState([]);
  const [workouts, setWorkouts] = useState(null);

  async function refresh() {
    const [catalog, day, currentProfile, planCatalog, workoutDay] = await Promise.all([
      apiCall('/api/foods'),
      apiCall('/api/dashboard'),
      apiCall('/api/profile'),
      apiCall('/api/workouts/plans'),
      apiCall('/api/workouts/today'),
    ]);
    setFoods(catalog);
    setDashboard(day);
    setProfile(currentProfile);
    setPlans(planCatalog);
    setWorkouts(workoutDay);
    setLoaded(true);
  }

  async function load() {
    setNotice('');
    try {
      await refresh();
    } catch (error) {
      setNotice(error.message);
    }
  }

  useEffect(() => {
    void load();
  }, []);

  function navigate(id) {
    setSection(id);
    setNavOpen(false);
  }

  const dateLabel = new Intl.DateTimeFormat('vi-VN', {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    timeZone: 'Asia/Ho_Chi_Minh',
  }).format(new Date());

  return (
    <div className="app-shell">
      <Header
        user={user}
        onHome={() => navigate('home')}
        onProfile={() => navigate('profile')}
        onLogout={logout}
        navOpen={navOpen}
        setNavOpen={setNavOpen}
        loggingOut={loggingOut}
      />
      <div className="body-layout">
        <Sidebar section={section} navOpen={navOpen} navigate={navigate} />
        <main className="content">
          <div className="page-intro">
            <div>
              <div className="date-line">
                <CalendarDays size={15} /> {dateLabel}
              </div>
              <h1>
                {section === 'home'
                  ? 'Tổng quan hôm nay'
                  : section === 'workout'
                    ? 'Tập luyện'
                    : section === 'profile'
                      ? 'Cá nhân'
                      : section === 'guide'
                        ? 'Hướng dẫn sử dụng'
                        : 'Ăn uống'}
              </h1>
              <p>
                {section === 'workout'
                  ? 'Chọn giáo án, tiếp tục buổi đang tập và theo dõi lịch đi tập/nghỉ.'
                  : section === 'profile'
                    ? 'Cập nhật thông tin và mục tiêu dinh dưỡng của bạn.'
                    : section === 'guide'
                      ? 'Thiết lập mục tiêu và làm quen với các chức năng chính.'
                      : 'Nhận diện món ăn, xác nhận khẩu phần và theo dõi thực đơn.'}
              </p>
            </div>
          </div>
          {notice && (
            <div className="global-notice" role="alert">
              {notice}
              <button className="link-button" onClick={load}>
                Thử tải lại
              </button>
              <button aria-label="Đóng thông báo" onClick={() => setNotice('')}>
                ×
              </button>
            </div>
          )}
          {!loaded ? (
            <p role="status">Đang tải thực đơn và danh mục món ăn…</p>
          ) : section === 'guide' ? (
            <GuidePanel onNavigate={navigate} />
          ) : section === 'profile' ? (
            <ProfilePanel profile={profile} call={apiCall} refresh={refresh} navigate={navigate} />
          ) : section === 'workout' ? (
            <div className="training-page">
              {workouts?.selected_plan && (
                <WorkoutPanel
                  workouts={workouts}
                  call={apiCall}
                  refresh={refresh}
                  onError={setNotice}
                />
              )}
              <WorkoutPlans
                plans={plans}
                selectedId={workouts?.selected_plan?.id}
                call={apiCall}
                refresh={refresh}
                onError={setNotice}
              />
            </div>
          ) : (
            <>
              <div className="dashboard-grid">
                <div className="main-column">
                  <ScanSection
                    call={apiCall}
                    foods={foods}
                    mealType={selectedMeal}
                    setMealType={setSelectedMeal}
                    onAdded={refresh}
                    onHistoryChange={() => setHistoryVersion((value) => value + 1)}
                  />
                  <ScanHistory call={apiCall} refreshKey={historyVersion} onError={setNotice} />
                </div>
                <div className="side-column">
                  <TodayMeals
                    dashboard={dashboard}
                    profile={profile}
                    setProfile={setProfile}
                    selectedMeal={selectedMeal}
                    call={apiCall}
                    refresh={refresh}
                    onError={setNotice}
                    onOpenProfile={() => navigate('profile')}
                  />
                </div>
              </div>
              <FoodHistory call={apiCall} refreshKey={dashboard} onError={setNotice} />
            </>
          )}
          <footer className="app-footer">
            Dinh dưỡng là số liệu ước tính. Hãy kiểm tra món và khẩu phần trước khi xác nhận.
          </footer>
        </main>
      </div>
    </div>
  );
}
