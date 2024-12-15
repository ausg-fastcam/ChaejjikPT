def format_minutes_to_hours_str(minutes: int) -> str:
    if minutes < 60:
        return f"{minutes}분"
    else:
        hours = minutes // 60  # 시간 계산
        remaining_minutes = minutes % 60  # 남은 분 계산
        if remaining_minutes == 0:
            return f"{hours}시간"
        else:
            return f"{hours}시간 {remaining_minutes}분"
