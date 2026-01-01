"""
批量上传辅助模块
提供批量上传的状态管理和处理逻辑
"""

import hashlib
from typing import List, Dict, Any, Tuple
from datetime import datetime


def generate_batch_id(uploaded_files) -> str:
    """
    根据文件列表生成唯一的批次ID
    使用文件名和大小的组合来生成哈希值
    """
    if not uploaded_files:
        return ""
    
    file_signatures = []
    for file in uploaded_files:
        file_signatures.append(f"{file.name}_{file.size}")
    
    batch_signature = "|".join(sorted(file_signatures))
    batch_hash = hashlib.md5(batch_signature.encode()).hexdigest()[:12]
    
    return f"batch_{batch_hash}"


def initialize_batch_state(uploaded_files, batch_id: str) -> Dict[str, Any]:
    """
    初始化批次状态
    返回一个包含所有文件初始状态的字典
    """
    files_state = {}
    
    for file in uploaded_files:
        file_key = f"{file.name}_{file.size}"
        files_state[file_key] = {
            'filename': file.name,
            'size': file.size,
            'status': 'pending',  # pending, processing, success, failed
            'error': None,
            'progress': 0.0,
            'upload_time': None
        }
    
    return {
        'batch_id': batch_id,
        'files': files_state,
        'batch_timestamp': datetime.now().isoformat(),
        'overall_status': 'idle',  # idle, processing, completed
        'total_files': len(uploaded_files),
        'completed_files': 0,
        'success_count': 0,
        'failed_count': 0
    }


def get_file_key(file) -> str:
    """获取文件的唯一标识符"""
    return f"{file.name}_{file.size}"


def update_file_status(batch_state: Dict, file_key: str, status: str, 
                       error: str = None, progress: float = None):
    """
    更新单个文件的状态
    """
    if file_key in batch_state['files']:
        batch_state['files'][file_key]['status'] = status
        
        if error:
            batch_state['files'][file_key]['error'] = error
        
        if progress is not None:
            batch_state['files'][file_key]['progress'] = progress
        
        # 更新统计信息
        if status == 'success':
            batch_state['files'][file_key]['upload_time'] = datetime.now().isoformat()
            batch_state['success_count'] = sum(
                1 for f in batch_state['files'].values() if f['status'] == 'success'
            )
        elif status == 'failed':
            batch_state['failed_count'] = sum(
                1 for f in batch_state['files'].values() if f['status'] == 'failed'
            )
        
        # 更新完成文件数
        batch_state['completed_files'] = sum(
            1 for f in batch_state['files'].values() 
            if f['status'] in ['success', 'failed']
        )
        
        # 更新整体状态
        if batch_state['completed_files'] == batch_state['total_files']:
            batch_state['overall_status'] = 'completed'
        elif batch_state['completed_files'] > 0:
            batch_state['overall_status'] = 'processing'


def get_pending_files(batch_state: Dict) -> List[str]:
    """获取所有待处理的文件键"""
    return [
        file_key for file_key, file_info in batch_state['files'].items()
        if file_info['status'] == 'pending'
    ]


def get_failed_files(batch_state: Dict) -> List[str]:
    """获取所有失败的文件键"""
    return [
        file_key for file_key, file_info in batch_state['files'].items()
        if file_info['status'] == 'failed'
    ]


def get_batch_progress(batch_state: Dict) -> float:
    """计算批次的整体进度 (0.0 - 1.0)"""
    if batch_state['total_files'] == 0:
        return 1.0
    
    return batch_state['completed_files'] / batch_state['total_files']


def get_batch_summary(batch_state: Dict) -> str:
    """生成批次处理摘要"""
    total = batch_state['total_files']
    success = batch_state['success_count']
    failed = batch_state['failed_count']
    pending = total - success - failed
    
    summary_parts = []
    
    if success > 0:
        summary_parts.append(f"✅ 成功: {success}")
    
    if failed > 0:
        summary_parts.append(f"❌ 失败: {failed}")
    
    if pending > 0:
        summary_parts.append(f"⏸️ 待处理: {pending}")
    
    return f"总计 {total} 个文件 - " + " | ".join(summary_parts)


def should_process_file(batch_state: Dict, file_key: str) -> bool:
    """
    判断文件是否应该被处理
    返回 True 表示需要处理（pending 或 failed 状态）
    """
    if file_key not in batch_state['files']:
        return False
    
    status = batch_state['files'][file_key]['status']
    return status in ['pending', 'failed']

