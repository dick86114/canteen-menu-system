"""
餐次分段识别器模块

用于识别横向格式Excel菜单中的餐次分段，支持智能的早餐、午餐、晚餐分类。
"""

import pandas as pd
import re
import logging
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class MealSegment:
    """餐次分段数据结构"""
    start_row: int      # 分段开始行
    end_row: int        # 分段结束行
    meal_type: str      # 餐次类型：'breakfast', 'lunch', 'dinner'
    confidence: float = 1.0  # 识别置信度


class MealSegmentIdentifier:
    """餐次分段识别器"""
    
    def __init__(self):
        # 餐次分隔符模式
        self.meal_separators = [
            '类别',           # 最常见的分隔符
            '早餐', '午餐', '晚餐',  # 明确的餐次标识
            'breakfast', 'lunch', 'dinner',  # 英文餐次标识
        ]
        
        # 餐次特征分类和关键词
        self.meal_indicators = {
            'breakfast': {
                'categories': ['粥品', '包点', '豆浆', '油条', '煎蛋', '早点', '粥类', '包子', '馒头'],
                'keywords': ['粥', '包', '豆浆', '油条', '蛋', '饼', '馒头', '豆腐脑', '小米', '大米']
            },
            'lunch': {
                'categories': ['荤菜', '素菜', '汤品', '主食', '米饭', '荤类', '素类', '肉类'],
                'keywords': ['肉', '鱼', '鸡', '猪', '牛', '菜', '汤', '炒', '烧', '炖', '蒸']
            },
            'dinner': {
                'categories': ['清淡', '小菜', '汤品', '粥品', '清炒', '蒸菜'],
                'keywords': ['清', '淡', '小菜', '汤', '粥', '蒸', '炒时蔬', '青菜']
            }
        }
    
    def identify_meal_segments(self, df: pd.DataFrame, weekday_row_idx: int) -> List[MealSegment]:
        """
        识别餐次分段
        
        Args:
            df: Excel数据DataFrame
            weekday_row_idx: 星期标题行的索引
            
        Returns:
            List[MealSegment]: 餐次分段列表
        """
        logger.info(f"开始识别餐次分段，星期行索引: {weekday_row_idx}")
        
        # 保存DataFrame引用供后续使用
        self._current_df = df
        
        segments = []
        current_segment_start = weekday_row_idx + 1
        current_meal_type = None
        
        # 从星期行之后开始扫描
        for row_idx in range(weekday_row_idx + 1, len(df)):
            first_col_value = str(df.iloc[row_idx, 0]).strip()
            
            # 检查是否是餐次分隔符
            if self._is_meal_separator(first_col_value, row_idx, df):
                logger.info(f"在第{row_idx}行发现分隔符: '{first_col_value}'")
                
                # 结束当前分段
                if current_segment_start < row_idx:
                    segment = MealSegment(
                        start_row=current_segment_start,
                        end_row=row_idx - 1,
                        meal_type=current_meal_type or self._infer_meal_type_from_content(
                            df, current_segment_start, row_idx - 1
                        )
                    )
                    segments.append(segment)
                    logger.info(f"创建分段: 行{segment.start_row}-{segment.end_row}, 类型: {segment.meal_type}")
                
                # 开始新分段
                current_segment_start = row_idx + 1
                current_meal_type = self._extract_meal_type_from_separator(first_col_value)
        
        # 处理最后一个分段
        if current_segment_start < len(df):
            segment = MealSegment(
                start_row=current_segment_start,
                end_row=len(df) - 1,
                meal_type=current_meal_type or self._infer_meal_type_from_content(
                    df, current_segment_start, len(df) - 1
                )
            )
            segments.append(segment)
            logger.info(f"创建最后分段: 行{segment.start_row}-{segment.end_row}, 类型: {segment.meal_type}")
        
        # 验证和调整分段结果
        validated_segments = self._validate_and_adjust_segments(segments)
        
        logger.info(f"餐次分段识别完成，共识别出 {len(validated_segments)} 个分段")
        return validated_segments
    
    def _is_meal_separator(self, cell_value: str, row_idx: int, df: pd.DataFrame) -> bool:
        """
        判断是否是餐次分隔符
        
        Args:
            cell_value: 单元格值
            row_idx: 行索引
            df: DataFrame
            
        Returns:
            bool: 是否为分隔符
        """
        # 空值或NaN
        if not cell_value or cell_value.lower() in ['nan', '']:
            return False
        
        # 明确的餐次标识
        if cell_value in self.meal_separators:
            return True
        
        # 检查是否是空行（整行都为空）
        if cell_value == 'nan' or not cell_value.strip():
            row_data = df.iloc[row_idx].astype(str)
            empty_cells = sum(1 for val in row_data if pd.isna(val) or str(val).strip() in ['', 'nan'])
            # 如果超过80%的单元格为空，认为是空行分隔符
            if empty_cells / len(row_data) > 0.8:
                return True
        
        return False
    
    def _extract_meal_type_from_separator(self, separator: str) -> Optional[str]:
        """
        从分隔符中提取餐次类型
        
        Args:
            separator: 分隔符文本
            
        Returns:
            Optional[str]: 餐次类型或None
        """
        meal_type_map = {
            '早餐': 'breakfast',
            'breakfast': 'breakfast',
            '午餐': 'lunch',
            '中餐': 'lunch',
            'lunch': 'lunch',
            '晚餐': 'dinner',
            'dinner': 'dinner'
        }
        
        return meal_type_map.get(separator)
    
    def _infer_meal_type_from_content(self, df: pd.DataFrame, start_row: int, end_row: int) -> str:
        """
        基于内容推断餐次类型
        
        Args:
            df: DataFrame
            start_row: 分段开始行
            end_row: 分段结束行
            
        Returns:
            str: 推断的餐次类型
        """
        content_text = ""
        
        # 收集分段内的所有文本内容
        for row_idx in range(start_row, end_row + 1):
            for col_idx in range(len(df.columns)):
                try:
                    cell_value = str(df.iloc[row_idx, col_idx]).strip()
                    if cell_value and cell_value != 'nan':
                        content_text += cell_value + " "
                except:
                    continue
        
        logger.debug(f"分段内容文本: {content_text[:100]}...")
        
        # 基于关键词匹配推断餐次
        scores = {'breakfast': 0, 'lunch': 0, 'dinner': 0}
        
        for meal_type, indicators in self.meal_indicators.items():
            # 分类名称匹配（权重更高）
            for category in indicators['categories']:
                if category in content_text:
                    scores[meal_type] += 3
                    logger.debug(f"分类匹配: {category} -> {meal_type} (+3)")
            
            # 关键词匹配
            for keyword in indicators['keywords']:
                keyword_count = content_text.count(keyword)
                if keyword_count > 0:
                    scores[meal_type] += keyword_count
                    logger.debug(f"关键词匹配: {keyword} x{keyword_count} -> {meal_type} (+{keyword_count})")
        
        # 返回得分最高的餐次类型
        best_meal = max(scores.items(), key=lambda x: x[1])
        logger.info(f"餐次推断结果: {best_meal[0]} (得分: {best_meal[1]})")
        
        return best_meal[0] if best_meal[1] > 0 else 'lunch'  # 默认午餐
    
    def _validate_and_adjust_segments(self, segments: List[MealSegment]) -> List[MealSegment]:
        """
        验证和调整分段结果
        
        Args:
            segments: 原始分段列表
            
        Returns:
            List[MealSegment]: 调整后的分段列表
        """
        if not segments:
            logger.warning("没有识别到任何分段")
            return segments
        
        logger.info(f"开始验证和调整 {len(segments)} 个分段")
        
        # 获取默认分配策略
        default_assignments = self.get_default_meal_assignment_strategy(len(segments))
        
        # 为每个分段分配餐次类型
        for i, segment in enumerate(segments):
            if i < len(default_assignments):
                # 使用位置提示进行高级推断
                position_hint = None
                if len(segments) > 1:
                    if i == 0:
                        position_hint = 'first'
                    elif i == len(segments) - 1:
                        position_hint = 'last'
                    else:
                        position_hint = 'middle'
                
                # 检查是否有明确的餐次标识符（如"早餐"、"午餐"、"晚餐"）
                has_explicit_meal_type = False
                if segment.meal_type in ['breakfast', 'lunch', 'dinner']:
                    # 检查这个餐次类型是否来自明确的分隔符
                    # 如果分段开始行的前一行包含餐次标识，则认为是明确的
                    if segment.start_row > 0:
                        prev_row_content = ""
                        try:
                            for col_idx in range(len(self._current_df.columns)):
                                cell_value = str(self._current_df.iloc[segment.start_row - 1, col_idx]).strip()
                                if cell_value and cell_value != 'nan':
                                    prev_row_content += cell_value + " "
                        except:
                            pass
                        
                        # 检查是否包含明确的餐次标识
                        explicit_indicators = ['早餐', '午餐', '晚餐', 'breakfast', 'lunch', 'dinner']
                        has_explicit_meal_type = any(indicator in prev_row_content for indicator in explicit_indicators)
                
                if has_explicit_meal_type:
                    # 保持明确标识的餐次类型
                    logger.info(f"分段{i+1}保持明确标识的餐次类型: {segment.meal_type}")
                else:
                    # 使用高级推断算法结合默认分配策略
                    content_text = self._extract_content_from_segment_range(segment.start_row, segment.end_row)
                    inferred_type, confidence = self.infer_meal_type_with_advanced_algorithm(
                        content_text, position_hint
                    )
                    
                    # 结合默认分配策略和推断结果
                    default_type = default_assignments[i]
                    
                    # 如果推断置信度较高且与默认分配一致，使用推断结果
                    if confidence > 0.5 and inferred_type == default_type:
                        segment.meal_type = inferred_type
                        segment.confidence = confidence
                        logger.info(f"分段{i+1}推断结果与默认分配一致: {segment.meal_type} (置信度: {confidence:.2f})")
                    # 如果推断置信度很高（>0.8），即使与默认不一致也使用推断结果
                    elif confidence > 0.8:
                        segment.meal_type = inferred_type
                        segment.confidence = confidence
                        logger.info(f"分段{i+1}高置信度推断: {segment.meal_type} (置信度: {confidence:.2f})")
                    else:
                        # 使用默认分配策略
                        segment.meal_type = default_type
                        segment.confidence = 0.5  # 默认置信度
                        logger.info(f"分段{i+1}使用默认分配: {segment.meal_type} (推断: {inferred_type}, 置信度: {confidence:.2f})")
        
        # 处理超过3个分段的情况
        if len(segments) > 3:
            logger.info(f"合并多余分段到晚餐")
            # 将第4个及以后的分段合并到第3个分段（晚餐）
            segments[2].end_row = segments[-1].end_row
            segments = segments[:3]
        
        return segments
    
    def _extract_content_from_segment_range(self, start_row: int, end_row: int) -> str:
        """
        从分段范围提取内容文本（用于推断）
        
        Args:
            start_row: 开始行
            end_row: 结束行
            
        Returns:
            str: 内容文本
        """
        if not hasattr(self, '_current_df'):
            return ""
        
        content_text = ""
        df = self._current_df
        
        # 收集分段内的所有文本内容
        for row_idx in range(start_row, end_row + 1):
            for col_idx in range(len(df.columns)):
                try:
                    cell_value = str(df.iloc[row_idx, col_idx]).strip()
                    if cell_value and cell_value != 'nan':
                        content_text += cell_value + " "
                except:
                    continue
        
        return content_text
    
    def _calculate_meal_type_score(self, segment: MealSegment, target_meal_type: str) -> float:
        """
        计算分段对特定餐次类型的匹配得分
        
        Args:
            segment: 餐次分段
            target_meal_type: 目标餐次类型
            
        Returns:
            float: 匹配得分
        """
        # 这里可以基于分段的内容特征计算得分
        # 简化实现，返回基础得分
        if target_meal_type in self.meal_indicators:
            return 1.0
        return 0.0
    
    def infer_meal_type_with_advanced_algorithm(self, content_text: str, position_hint: str = None) -> Tuple[str, float]:
        """
        高级餐次推断算法
        
        Args:
            content_text: 内容文本
            position_hint: 位置提示 ('first', 'middle', 'last')
            
        Returns:
            Tuple[str, float]: (餐次类型, 置信度)
        """
        scores = {'breakfast': 0.0, 'lunch': 0.0, 'dinner': 0.0}
        
        # 1. 基于内容特征的评分
        for meal_type, indicators in self.meal_indicators.items():
            # 分类名称匹配（高权重）
            for category in indicators['categories']:
                if category in content_text:
                    scores[meal_type] += 5.0
            
            # 关键词匹配（中权重）
            for keyword in indicators['keywords']:
                keyword_count = content_text.count(keyword)
                scores[meal_type] += keyword_count * 2.0
        
        # 2. 基于位置的调整
        if position_hint:
            if position_hint == 'first':
                scores['breakfast'] += 2.0  # 第一个分段更可能是早餐
            elif position_hint == 'middle':
                scores['lunch'] += 2.0      # 中间分段更可能是午餐
            elif position_hint == 'last':
                scores['dinner'] += 2.0     # 最后分段更可能是晚餐
        
        # 3. 特殊规则调整
        # 如果包含"粥"但也有"肉"，可能是午餐而不是早餐
        if '粥' in content_text and any(meat in content_text for meat in ['肉', '鸡', '鱼']):
            scores['breakfast'] *= 0.7
            scores['lunch'] += 1.0
        
        # 如果包含"清淡"或"小菜"，更可能是晚餐
        if any(light in content_text for light in ['清淡', '小菜', '清炒']):
            scores['dinner'] += 3.0
        
        # 计算最佳匹配
        best_meal = max(scores.items(), key=lambda x: x[1])
        confidence = best_meal[1] / (sum(scores.values()) + 1e-6)  # 避免除零
        
        return best_meal[0], min(confidence, 1.0)
    
    def get_default_meal_assignment_strategy(self, segment_count: int) -> List[str]:
        """
        获取默认餐次分配策略
        
        Args:
            segment_count: 分段数量
            
        Returns:
            List[str]: 餐次类型列表
        """
        strategies = {
            1: ['lunch'],                           # 1个分段 -> 午餐
            2: ['breakfast', 'lunch'],              # 2个分段 -> 早餐+午餐
            3: ['breakfast', 'lunch', 'dinner'],    # 3个分段 -> 早餐+午餐+晚餐
        }
        
        if segment_count <= 3:
            return strategies[segment_count]
        else:
            # 超过3个分段，前3个按早午晚，其余合并到晚餐
            return ['breakfast', 'lunch', 'dinner'] + ['dinner'] * (segment_count - 3)