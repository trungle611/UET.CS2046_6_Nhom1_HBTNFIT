import React, { useState } from 'react';
import { Check, Sparkles, Settings2 } from 'lucide-react';
import { MEAL_LABELS } from './constants.js';

const defaults = {
  age: '',
  height_cm: '',
  weight_kg: '',
  target_weight_kg: '',
  target_date: '',
  sex: 'male',
  activity_level: 'moderate',
  protein_mode: 'balanced',
  goal: 'maintain',
};
const numberFields = [
  ['age', 'Tuổi', 18, 120, 1],
  ['height_cm', 'Chiều cao (cm)', 100, 250, 0.1],
  ['weight_kg', 'Cân nặng hiện tại (kg)', 25, 400, 0.1],
  ['target_weight_kg', 'Cân nặng mong muốn (kg)', 25, 400, 0.1],
];
const fmt = (value) => Number(value).toLocaleString('vi-VN');

export default function ProfilePanel({ profile, call, refresh, navigate }) {
  const [form, setForm] = useState(() => ({
    ...defaults,
    ...Object.fromEntries(Object.keys(defaults).map((key) => [key, profile[key] ?? defaults[key]])),
    avoid: (profile.avoid_tags || []).join(', '),
  }));
  const [targets, setTargets] = useState(profile.daily_targets);
  const [dirty, setDirty] = useState(false);
  const [busy, setBusy] = useState('');
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');
  const analysis = !dirty && profile.analysis;
  const today = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Ho_Chi_Minh',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(new Date());
  const tomorrow = new Date(`${today}T00:00:00+07:00`);
  tomorrow.setUTCDate(tomorrow.getUTCDate() + 1);
  const minDate = new Intl.DateTimeFormat('en-CA', {
    timeZone: 'Asia/Ho_Chi_Minh',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  }).format(tomorrow);

  function update(key, value) {
    setForm((current) => ({ ...current, [key]: value }));
    setDirty(true);
    setTargets(null);
    setError('');
    setMessage('');
  }
  function payload() {
    // Chỉ gửi các trường nhập; không gửi analysis/daily_targets từ response về API.
    const value = Object.fromEntries(Object.keys(defaults).map((key) => [key, form[key]]));
    for (const [key] of numberFields) value[key] = Number(value[key]);
    const difference = value.target_weight_kg - value.weight_kg;
    const expected = difference > 0.1 ? 'gain' : difference < -0.1 ? 'lose' : 'maintain';
    if (value.goal !== expected)
      throw new Error('Mục tiêu tăng/giảm/duy trì phải khớp với cân nặng mong muốn.');
    value.avoid_tags = [
      ...new Set(
        form.avoid
          .split(/[,;\n]/)
          .map((s) => s.trim())
          .filter(Boolean),
      ),
    ];
    value.target_kcal = profile.target_kcal || 1800;
    return value;
  }
  async function submit(event) {
    event.preventDefault();
    const action = event.nativeEvent.submitter?.value || 'save';
    setBusy(action);
    setError('');
    setMessage('');
    try {
      const body = JSON.stringify(payload());
      const options = { headers: { 'Content-Type': 'application/json' }, body };
      if (action === 'preview') {
        const result = await call('/api/profile/preview', { ...options, method: 'POST' });
        setTargets(result.daily_targets);
        setMessage('Đây là kết quả tính thử. Nhấn Lưu và tính mục tiêu để áp dụng vào Ăn uống.');
      } else {
        const result = await call('/api/profile', { ...options, method: 'PUT' });
        setTargets(result.daily_targets);
        setDirty(false);
        await refresh();
        setMessage('Đã lưu mục tiêu và cập nhật bốn chỉ số trong Ăn uống.');
        if (action === 'food') navigate('food');
        if (action === 'analyze') {
          await call('/api/profile/analyze', { method: 'POST' });
          await refresh();
          setMessage('Đã tạo gợi ý. Chọn phương án phù hợp bên dưới.');
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  }
  async function choose(key, id, section) {
    setBusy(id);
    setError('');
    try {
      await call('/api/profile/choice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ [key]: id }),
      });
      await refresh();
      navigate(section);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy('');
    }
  }
  const view = { ...profile, ...form, daily_targets: targets, analysis };
  const currentWeight = Number(form.weight_kg);
  const targetWeight = Number(form.target_weight_kg);
  const expectedGoal =
    currentWeight > 0 && targetWeight > 0
      ? targetWeight - currentWeight > 0.1
        ? 'gain'
        : targetWeight - currentWeight < -0.1
          ? 'lose'
          : 'maintain'
      : null;
  const goalMismatch = !!expectedGoal && form.goal !== expectedGoal;
  const goalLabels = { gain: 'Tăng cân', lose: 'Giảm cân', maintain: 'Duy trì' };
  return (
    <div className="profile-page">
      <section className="panel profile-panel">
        <div className="panel-heading">
          <div>
            <div className="section-kicker">
              <Settings2 size={15} /> THÔNG TIN CÁ NHÂN
            </div>
            <h2>Hồ sơ của bạn</h2>
          </div>
        </div>
        <p className="panel-lead">
          Nhập cân nặng hiện tại và mong muốn để nhận các phương án tham khảo. Hồ sơ và lịch sử được
          lưu riêng theo tài khoản.
        </p>
        <form onSubmit={submit}>
          <fieldset disabled={!!busy} className="profile-fieldset">
            <div className="profile-grid">
              <label>
                Tuổi
                <input
                  type="number"
                  min="18"
                  max="120"
                  required
                  name="age"
                  value={view.age ?? ''}
                  onChange={(e) => update('age', e.target.value)}
                  placeholder="Ví dụ 22"
                />
              </label>
              <label>
                Chiều cao (cm)
                <input
                  type="number"
                  min="100"
                  max="250"
                  step="0.1"
                  required
                  name="height_cm"
                  value={view.height_cm ?? ''}
                  onChange={(e) => update('height_cm', e.target.value)}
                  placeholder="Ví dụ 170"
                />
              </label>
              <label>
                Cân nặng hiện tại (kg)
                <input
                  type="number"
                  min="25"
                  max="400"
                  step="0.1"
                  required
                  name="weight_kg"
                  value={view.weight_kg ?? ''}
                  onChange={(e) => update('weight_kg', e.target.value)}
                  placeholder="Ví dụ 65"
                />
              </label>
              <label>
                Cân nặng mong muốn (kg)
                <input
                  type="number"
                  min="25"
                  max="400"
                  step="0.1"
                  required
                  name="target_weight_kg"
                  value={view.target_weight_kg ?? ''}
                  onChange={(e) => update('target_weight_kg', e.target.value)}
                  placeholder="Ví dụ 70"
                />
              </label>
              <label>
                Muốn đạt mục tiêu trước ngày
                <input
                  type="date"
                  required
                  min={minDate}
                  name="target_date"
                  value={view.target_date ?? ''}
                  onInput={(e) => update('target_date', e.target.value)}
                  onChange={(e) => update('target_date', e.target.value)}
                />
              </label>
              <label>
                Mục tiêu
                <select
                  name="goal"
                  value={view.goal || 'maintain'}
                  onChange={(e) => update('goal', e.target.value)}
                >
                  <option value="maintain">Duy trì</option>
                  <option value="gain">Tăng cân</option>
                  <option value="lose">Giảm cân</option>
                </select>
              </label>
              <label>
                Thông số sinh học để ước tính năng lượng
                <select
                  name="sex"
                  value={view.sex ?? ''}
                  onChange={(e) => update('sex', e.target.value || null)}
                >
                  <option value="">Chọn nếu muốn tính mục tiêu</option>
                  <option value="female">Nữ</option>
                  <option value="male">Nam</option>
                </select>
              </label>
              <label>
                Mức vận động hiện tại
                <select
                  name="activity_level"
                  value={view.activity_level ?? ''}
                  onChange={(e) => update('activity_level', e.target.value || null)}
                >
                  <option value="">Chọn mức vận động</option>
                  <option value="sedentary">Ít vận động</option>
                  <option value="light">Nhẹ · 1–3 buổi/tuần</option>
                  <option value="moderate">Vừa · 3–5 buổi/tuần</option>
                  <option value="high">Nhiều · 6–7 buổi/tuần</option>
                </select>
              </label>
              <label>
                Mức protein muốn theo dõi
                <select
                  name="protein_mode"
                  value={view.protein_mode || 'balanced'}
                  onChange={(e) => update('protein_mode', e.target.value)}
                >
                  <option value="balanced">Cân bằng · khoảng 1,2 g/kg</option>
                  <option value="strength">Tập kháng lực đều · khoảng 1,6 g/kg</option>
                </select>
              </label>
              <label>
                Thành phần cần tránh
                <input
                  value={form.avoid}
                  onChange={(e) => update('avoid', e.target.value)}
                  name="avoid"
                  maxLength={500}
                  placeholder="Ví dụ: tôm, thịt heo"
                />
              </label>
            </div>
            {view.daily_targets && (
              <div className="goal-estimate">
                <div>
                  <strong>{view.daily_targets.kcal.toLocaleString('vi-VN')} kcal</strong>
                  <span>Mỗi ngày</span>
                </div>
                <div>
                  <strong>{view.daily_targets.protein_g} g</strong>
                  <span>Protein</span>
                </div>
                <div>
                  <strong>{view.daily_targets.carb_g ?? '–'} g</strong>
                  <span>Carb</span>
                </div>
                <div>
                  <strong>{view.daily_targets.fat_g ?? '–'} g</strong>
                  <span>Chất béo</span>
                </div>
                <div>
                  <strong>{view.daily_targets.days_remaining} ngày</strong>
                  <span>Đến thời hạn đã chọn</span>
                </div>
              </div>
            )}
            {view.daily_targets && (
              <p className="data-note">
                Protein: {view.weight_kg} kg × {view.daily_targets.protein_factor} g/kg ≈{' '}
                {view.daily_targets.protein_g} g/ngày. Mức này theo cách tập bạn chọn, không tăng
                theo số kg muốn đạt.
              </p>
            )}
            {view.daily_targets?.timeline_warning && (
              <p className="goal-warning">
                Thời hạn này có thể quá gấp. Mức ăn gợi ý đã được giới hạn; không đảm bảo đạt đúng
                cân nặng vào ngày chọn.
              </p>
            )}
            {view.daily_targets?.macro_distribution_warning && (
              <p className="goal-warning">
                Mức kcal và protein đã chọn khiến tỷ lệ carb thấp hơn khoảng tham khảo. Hãy xem lại
                mục tiêu hoặc trao đổi với chuyên gia dinh dưỡng.
              </p>
            )}
            {goalMismatch && (
              <p className="goal-warning">
                Cân nặng mong muốn này tương ứng với mục tiêu <b>{goalLabels[expectedGoal]}</b>. Hãy
                chọn lại trường Mục tiêu trước khi lưu.
              </p>
            )}
            <div className="profile-footer">
              <button
                className="primary-button"
                disabled={!!busy || goalMismatch}
                name="action"
                value="save"
              >
                Lưu và tính mục tiêu
              </button>
              <button
                className="secondary-button"
                disabled={!!busy || goalMismatch}
                name="action"
                value="analyze"
              >
                <Sparkles size={16} />
                {busy === 'analyze' ? 'Đang phân tích…' : 'AI gợi ý ăn uống & tập luyện'}
              </button>
              <button
                className="secondary-button"
                name="action"
                value="preview"
                disabled={!!busy || goalMismatch}
              >
                Tính thử
              </button>
              <button
                className="secondary-button"
                name="action"
                value="food"
                disabled={!!busy || goalMismatch}
              >
                Lưu và xem ăn uống
              </button>
            </div>
            <p className="data-note">
              Điền đủ tuổi, chiều cao, hai mức cân nặng, thời hạn, thông số sinh học và mức vận động
              để tính. Kcal và protein là ước tính tham khảo, không thay thế tư vấn chuyên môn.
            </p>
          </fieldset>
        </form>
        {error && (
          <p className="goal-warning" role="alert">
            {error}
          </p>
        )}
        {message && (
          <p className="data-note" role="status">
            {message}
          </p>
        )}
      </section>
      {view.analysis && (
        <section className="panel guidance-panel">
          <div className="section-kicker">
            <Sparkles size={15} /> GỢI Ý TỪ GEMINI
          </div>
          <h2>Phương án cho mục tiêu của bạn</h2>
          <p className="panel-lead">{view.analysis.summary}</p>
          <h3>Ăn uống</h3>
          <div className="guidance-grid">
            {view.analysis.food_options?.map((option) => (
              <article
                className={`guidance-card ${view.food_choice === option.id ? 'selected' : ''}`}
                key={option.id}
              >
                <h4>{option.title}</h4>
                <p>{option.detail}</p>
                {option.estimated_totals && (
                  <div className="guidance-total">
                    <b>≈ {option.estimated_totals.kcal.toLocaleString('vi-VN')} kcal/ngày</b>
                    <span>
                      P {option.estimated_totals.protein}g · C {option.estimated_totals.carb}g · F{' '}
                      {option.estimated_totals.fat}g
                    </span>
                  </div>
                )}
                <ul>
                  {option.examples?.map((example, index) => (
                    <li key={index}>
                      {typeof example === 'string' ? (
                        example
                      ) : (
                        <>
                          <b>{MEAL_LABELS[example.meal_type]}:</b> {example.name} ·{' '}
                          {example.default_amount} {example.unit}
                        </>
                      )}
                    </li>
                  ))}
                </ul>
                <button
                  className="secondary-button"
                  disabled={!!busy || view.food_choice === option.id}
                  onClick={() => choose('food_choice', option.id, 'food')}
                >
                  {view.food_choice === option.id ? (
                    <>
                      <Check size={15} /> Đã chọn
                    </>
                  ) : (
                    'Chọn cách ăn này'
                  )}
                </button>
              </article>
            ))}
          </div>
          <h3>Tập luyện</h3>
          <div className="guidance-grid">
            {view.analysis.workout_options?.map((option) => (
              <article
                className={`guidance-card ${view.workout_choice === option.id ? 'selected' : ''}`}
                key={option.id}
              >
                <h4>{option.name}</h4>
                <p>{option.detail}</p>
                <button
                  className="secondary-button"
                  disabled={!!busy || view.workout_choice === option.id}
                  onClick={() => choose('workout_choice', option.id, 'workout')}
                >
                  {view.workout_choice === option.id ? (
                    <>
                      <Check size={15} /> Đã chọn
                    </>
                  ) : (
                    'Chọn giáo án này'
                  )}
                </button>
              </article>
            ))}
          </div>
          <p className="data-note">
            Gợi ý được tạo bằng {view.analysis.model}; định lượng được hệ thống cân chỉnh theo kcal
            mục tiêu và vẫn chỉ mang tính tham khảo.
          </p>
        </section>
      )}
    </div>
  );
}
