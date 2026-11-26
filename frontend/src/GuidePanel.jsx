import React from 'react';
import {
  Camera,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  Dumbbell,
  Target,
  UtensilsCrossed,
} from 'lucide-react';

const steps = [
  {
    number: '01',
    icon: Target,
    title: 'Nhập mục tiêu cá nhân',
    section: 'profile',
    action: 'Mở mục Cá nhân',
    items: [
      'Nhập tuổi, chiều cao và cân nặng hiện tại.',
      'Chọn cân nặng mong muốn và ngày muốn hoàn thành.',
      'Chọn mục tiêu, giới tính, mức vận động và mức protein.',
      'Nhấn “Lưu và tính mục tiêu”.',
    ],
  },
  {
    number: '02',
    icon: ClipboardCheck,
    title: 'Kiểm tra chỉ tiêu mỗi ngày',
    section: 'profile',
    action: 'Xem mục tiêu',
    items: [
      'Xem kcal, protein, carb và chất béo cần theo dõi.',
      'Nếu thời hạn quá gấp, hệ thống sẽ hiển thị cảnh báo.',
      'Có thể dùng “AI gợi ý ăn uống & tập luyện” để xem phương án tham khảo.',
    ],
  },
  {
    number: '03',
    icon: Camera,
    title: 'Quét ảnh bữa ăn',
    section: 'food',
    action: 'Mở Ăn uống',
    items: [
      'Kéo thả ảnh hoặc nhấn “Tải ảnh”.',
      'Chờ Gemini nhận diện các món trong ảnh.',
      'Kiểm tra tên món, khẩu phần và dinh dưỡng trước khi lưu.',
    ],
  },
  {
    number: '04',
    icon: UtensilsCrossed,
    title: 'Xác nhận và quản lý thực đơn',
    section: 'food',
    action: 'Xem thực đơn',
    items: [
      'Sửa món AI nhận sai hoặc nhập món chưa có trong danh mục.',
      'Chọn bữa sáng, trưa, tối hoặc bữa phụ.',
      'Nhấn “Xác nhận thêm”; món chưa xác nhận không được cộng vào tổng.',
      'Có thể sửa khẩu phần hoặc xóa món đã thêm.',
    ],
  },
  {
    number: '05',
    icon: Dumbbell,
    title: 'Chọn giáo án tập luyện',
    section: 'workout',
    action: 'Mở Tập luyện',
    items: [
      'Chọn nhóm Tăng cơ hoặc Giảm cân.',
      'Chọn PPL hoặc Upper/Lower phù hợp.',
      'Mở từng buổi để xem tên bài, nhóm cơ, số hiệp và số lần.',
    ],
  },
  {
    number: '06',
    icon: CheckCircle2,
    title: 'Theo dõi buổi tập',
    section: 'workout',
    action: 'Theo dõi tập luyện',
    items: [
      'Ghi nhận “Có đi tập” hoặc “Bỏ lỡ hôm nay”.',
      'Nhấn “Xem chi tiết” để đọc hướng dẫn từng bài.',
      'Bắt đầu và đánh dấu hoàn thành từng bài; hoàn thành cả buổi để chuyển sang buổi kế tiếp.',
    ],
  },
];

export default function GuidePanel({ onNavigate }) {
  return (
    <section className="guide-page" aria-labelledby="guide-title">
      <div className="guide-intro">
        <span className="section-kicker">BẮT ĐẦU VỚI HBTNFIT</span>
        <h2 id="guide-title">Quy trình sử dụng đề xuất</h2>
        <p>
          Thiết lập mục tiêu trước, sau đó theo dõi ăn uống và tập luyện hằng ngày. Bạn có thể quay
          lại chỉnh mục tiêu bất cứ lúc nào.
        </p>
        <button className="primary-button" onClick={() => onNavigate('profile')}>
          <Target size={17} /> Nhập mục tiêu ngay
        </button>
      </div>
      <div className="guide-flow">
        {steps.map(({ number, icon: Icon, title, section, action, items }, index) => (
          <article className="guide-step" key={number}>
            <div className="guide-marker">
              <span>{number}</span>
              {index < steps.length - 1 && <i />}
            </div>
            <div className="guide-card">
              <div className="guide-card-heading">
                <span className="guide-icon">
                  <Icon size={19} />
                </span>
                <div>
                  <small>BƯỚC {number}</small>
                  <h3>{title}</h3>
                </div>
              </div>
              <ul>
                {items.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
              <button className="guide-action" onClick={() => onNavigate(section)}>
                {action}
                <ChevronRight size={15} />
              </button>
            </div>
          </article>
        ))}
      </div>
      <div className="guide-tip">
        <strong>Lưu ý</strong>
        <p>
          Các chỉ số dinh dưỡng và giáo án chỉ mang tính tham khảo. Hãy điều chỉnh theo thể lực và
          dừng tập nếu cảm thấy đau hoặc không thoải mái.
        </p>
      </div>
    </section>
  );
}
