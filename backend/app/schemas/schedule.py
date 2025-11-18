from datetime import date as DateType, time as TimeType, datetime
from pydantic import BaseModel, ConfigDict, field_validator

class ScheduleBase(BaseModel):
    """일정의 기본 필드를 정의하는 스키마"""
    title: str
    date: DateType
    content: str | None = None
    start_time: TimeType
    end_time: TimeType
    
    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('제목은 비어있을 수 없습니다')
        return v.strip()
    
    @field_validator('end_time')
    @classmethod
    def validate_time_range(cls, v: TimeType | None, info) -> TimeType | None:
        if v and info.data.get('start_time'):
            if v <= info.data['start_time']:
                raise ValueError('종료 시간은 시작 시간보다 늦어야 합니다')
        return v

class ScheduleCreate(ScheduleBase):
    """일정 생성 시 사용되는 스키마"""
    pass

class ScheduleUpdate(BaseModel):
    """일정 수정 시 사용되는 스키마"""
    title: str | None = None
    date: DateType | None = None
    content: str | None = None
    start_time: TimeType | None = None
    end_time: TimeType | None = None

class ScheduleResponse(ScheduleBase):
    """API 응답으로 사용되는 스키마"""
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )
    

# 토막 상식
## fastAPI와 pydantic은 datetime.date 객체를 ISO 8601 형식의 문자열("2025-11-18")로 자동 직렬화하여 JSON 응답을 보냅니다.
