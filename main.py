#!/usr/bin/env python3
import os
import sys
import json
import shutil
from datetime import datetime
from modules.questionnaire import DailyQuestionnaire
from modules.scoring import ScoringSystem
from modules.data_manager import DataManager
from modules.report_generator import ReportGenerator
from modules.excel_handler import ExcelHandler
from modules.redemption_system import RedemptionSystem


class StudyDiary:
    def __init__(self):
        self.questionnaire = DailyQuestionnaire()
        self.scoring = ScoringSystem()
        self.data_manager = DataManager()
        self.report_generator = ReportGenerator(self.data_manager)
        self.excel_handler = ExcelHandler()
        self.redemption_system = RedemptionSystem(self.data_manager)
    
    def run(self):
        print("=" * 60)
        print("🎯 ZZW考公学习日记系统")
        print("=" * 60)
        print()
        
        while True:
            self.show_menu()
            choice = input("\n请选择操作 (输入数字): ").strip()
            
            if choice == '1':
                self.export_questionnaire_excel()
            elif choice == '2':
                self.import_questionnaire_excel()
            elif choice == '3':
                self.view_redemption_shop()
            elif choice == '4':
                self.redeem_reward()
            elif choice == '5':
                self.view_today_report()
            elif choice == '6':
                self.view_points_history()
            elif choice == '7':
                self.view_statistics()
            elif choice == '8':
                self.generate_weekly_summary()
            elif choice == '9':
                self.visualize_progress()
            elif choice == '10':
                self.export_data()
            elif choice == '0':
                print("\n👋 再见！继续加油，考公必胜！")
                break
            else:
                print("\n❌ 无效选择，请重新输入")
    
    def show_menu(self):
        total_points = self.data_manager.get_total_points()
        print("\n📋 主菜单:")
        print(f"💰 当前积分: {total_points}分")
        print("-" * 40)
        print("1. 📤 导出今日问卷 (Excel)")
        print("2. 📥 导入问卷答案 (Excel)")
        print("3. 🎁 查看积分商城")
        print("4. 🛒 兑换奖励")
        print("5. 📄 查看今日报告")
        print("6. 📊 查看积分历史")
        print("7. 📈 查看学习统计")
        print("8. 📅 生成周总结")
        print("9. 📉 可视化进度")
        print("10. 💾 导出数据")
        print("0. 退出系统")
    
    def export_questionnaire_excel(self):
        print("\n" + "=" * 50)
        print("📤 导出今日问卷到Excel")
        print("=" * 50)
        
        questions = self.questionnaire.generate_questionnaire()
        filepath = self.excel_handler.export_questionnaire(questions)
        
        print(f"\n✅ 问卷已导出: {filepath}")
        print("\n📝 请将此文件发送给ZZW进行填写")
        print("📌 填写完成后，使用菜单选项2导入答案")
    
    def import_questionnaire_excel(self):
        print("\n" + "=" * 50)
        print("📥 导入问卷答案")
        print("=" * 50)
        
        # 显示可用的Excel文件
        questionnaire_dir = self.excel_handler.questionnaire_dir
        files = [f for f in os.listdir(questionnaire_dir) 
                if f.endswith('.xlsx') and f.startswith('daily_questionnaire_')]
        
        if not files:
            print("\n❌ 没有找到问卷文件")
            print("请先使用选项1导出问卷")
            return
        
        print("\n可用的问卷文件:")
        for i, file in enumerate(sorted(files, reverse=True)):
            print(f"{i+1}. {file}")
        
        choice = input("\n请选择文件编号 (或输入完整路径): ").strip()
        
        if choice.isdigit() and 1 <= int(choice) <= len(files):
            filepath = os.path.join(questionnaire_dir, sorted(files, reverse=True)[int(choice)-1])
        else:
            filepath = choice
        
        if not os.path.exists(filepath):
            print(f"\n❌ 文件不存在: {filepath}")
            return
        
        # 验证文件
        if not self.excel_handler.validate_excel_file(filepath):
            print("\n❌ 文件格式不正确或没有填写答案")
            return
        
        try:
            # 导入答案
            questions = self.questionnaire.generate_questionnaire()
            responses = self.excel_handler.import_answers(filepath, questions)
            
            # 处理响应
            processed_responses = self.questionnaire.process_responses(responses)
            
            # 保存响应
            self.data_manager.save_response(processed_responses)
            
            # 计算积分
            historical_data = self.data_manager.get_recent_responses(30)
            points, point_details = self.scoring.calculate_points(processed_responses, historical_data)
            
            # 更新积分
            self.data_manager.update_points(processed_responses["date"], points, point_details)
            
            # 获取等级信息
            total_points = self.data_manager.get_total_points()
            level_info = self.scoring.get_level_info(total_points)
            
            # 生成报告
            print("\n⏳ 正在生成每日总结报告...")
            report_path = self.report_generator.generate_report(
                processed_responses, point_details, total_points, level_info
            )
            
            # 显示结果
            print("\n" + "=" * 50)
            print("✅ 问卷导入成功！")
            print(f"📊 今日得分: {points:+d}分")
            print(f"💰 总积分: {total_points}分")
            print(f"🏆 当前等级: {level_info['current']['emoji']} {level_info['current']['name']}")
            
            if level_info['next']:
                print(f"📈 距离下一等级还需: {level_info['needed']}分")
            
            encouragement = self.scoring.get_encouragement_message(total_points, points)
            print(f"\n{encouragement}")
            
            print(f"\n📄 报告已生成: {report_path}")
            
            # 移动已处理的文件到已回答文件夹
            answered_dir = os.path.join(questionnaire_dir, "answered")
            os.makedirs(answered_dir, exist_ok=True)
            
            answered_path = os.path.join(answered_dir, os.path.basename(filepath))
            shutil.move(filepath, answered_path)
            print(f"\n📁 已将问卷移至: {answered_path}")
            
        except Exception as e:
            print(f"\n❌ 导入失败: {e}")
    
    def view_redemption_shop(self):
        print("\n" + "=" * 50)
        print("🎁 积分兑换商城")
        print("=" * 50)
        
        total_points = self.data_manager.get_total_points()
        print(f"\n💰 当前可用积分: {total_points}分")
        
        # 显示可兑换的奖励
        available_rewards = self.redemption_system.get_available_rewards(total_points)
        
        if not available_rewards:
            print("\n😔 当前积分还不够兑换任何奖励，继续加油！")
        else:
            print(f"\n✨ 你可以兑换以下{len(available_rewards)}项奖励:")
            print("-" * 40)
            
            for i, reward in enumerate(available_rewards):
                print(f"{i+1}. {reward['emoji']} {reward['name']} - {reward['points']}分")
                print(f"   {reward['description']}")
                print()
        
        # 显示全部奖励列表
        print("\n📜 查看完整奖励列表:")
        rewards_display = self.redemption_system.format_rewards_display()
        print(rewards_display)
        
        # 显示兑换统计
        stats = self.redemption_system.get_redemption_stats()
        if stats['total_redemptions'] > 0:
            print("\n📊 兑换统计:")
            print(f"总兑换次数: {stats['total_redemptions']}次")
            print(f"累计消耗积分: {stats['total_points_spent']}分")
    
    def redeem_reward(self):
        print("\n" + "=" * 50)
        print("🛒 兑换奖励")
        print("=" * 50)
        
        total_points = self.data_manager.get_total_points()
        print(f"\n💰 当前可用积分: {total_points}分")
        
        available_rewards = self.redemption_system.get_available_rewards(total_points)
        
        if not available_rewards:
            print("\n😔 当前积分还不够兑换任何奖励")
            return
        
        print("\n可兑换的奖励:")
        for i, reward in enumerate(available_rewards):
            print(f"{i+1}. {reward['emoji']} {reward['name']} - {reward['points']}分")
        
        choice = input("\n请选择要兑换的奖励编号 (0取消): ").strip()
        
        if choice == '0':
            print("\n已取消兑换")
            return
        
        if not choice.isdigit() or int(choice) < 1 or int(choice) > len(available_rewards):
            print("\n❌ 无效的选择")
            return
        
        reward = available_rewards[int(choice) - 1]
        
        # 确认兑换
        confirm = input(f"\n确认要兑换 '{reward['name']}' 吗？将消耗 {reward['points']} 积分 (y/n): ").strip().lower()
        
        if confirm != 'y':
            print("\n已取消兑换")
            return
        
        # 执行兑换
        success, message = self.redemption_system.redeem_reward(reward['id'])
        
        if success:
            print(f"\n🎉 {message}")
            print(f"💰 剩余积分: {self.data_manager.get_total_points()}分")
            print("\n请记得完成兑换的奖励哦！享受你的奖励吧！")
        else:
            print(f"\n❌ {message}")
    
    def fill_daily_questionnaire(self):
        print("\n" + "=" * 50)
        print("📝 开始填写今日学习问卷")
        print("=" * 50)
        
        # 获取问卷
        questions = self.questionnaire.generate_questionnaire()
        responses = {}
        
        # 收集答案
        for i, question in enumerate(questions):
            if question["type"] == "auto":
                continue
            
            print(f"\n问题 {i}: {question['question']}")
            
            if question["type"] == "choice":
                for j, option in enumerate(question["options"]):
                    print(f"  {j}. {option}")
                
                while True:
                    try:
                        answer = int(input("请选择 (输入数字): "))
                        if 0 <= answer < len(question["options"]):
                            responses[question["id"]] = answer
                            break
                        else:
                            print("❌ 请输入有效的选项编号")
                    except ValueError:
                        print("❌ 请输入数字")
            
            elif question["type"] == "text":
                answer = input(f"请输入 ({question.get('placeholder', '')}): ").strip()
                if answer:
                    responses[question["id"]] = answer
        
        # 处理响应
        processed_responses = self.questionnaire.process_responses(responses)
        
        # 保存响应
        self.data_manager.save_response(processed_responses)
        
        # 计算积分
        historical_data = self.data_manager.get_recent_responses(30)
        points, point_details = self.scoring.calculate_points(processed_responses, historical_data)
        
        # 更新积分
        self.data_manager.update_points(processed_responses["date"], points, point_details)
        
        # 获取等级信息
        total_points = self.data_manager.get_total_points()
        level_info = self.scoring.get_level_info(total_points)
        
        # 生成报告
        print("\n⏳ 正在生成每日总结报告...")
        report_path = self.report_generator.generate_report(
            processed_responses, point_details, total_points, level_info
        )
        
        # 显示结果
        print("\n" + "=" * 50)
        print("✅ 问卷填写完成！")
        print(f"📊 今日得分: {points:+d}分")
        print(f"💰 总积分: {total_points}分")
        print(f"🏆 当前等级: {level_info['current']['emoji']} {level_info['current']['name']}")
        
        if level_info['next']:
            print(f"📈 距离下一等级还需: {level_info['needed']}分")
        
        encouragement = self.scoring.get_encouragement_message(total_points, points)
        print(f"\n{encouragement}")
        
        print(f"\n📄 报告已生成: {report_path}")
    
    def view_today_report(self):
        today = datetime.now().strftime("%Y-%m-%d")
        response = self.data_manager.get_response_by_date(today)
        
        if not response:
            print("\n❌ 今天还没有填写问卷哦！请先填写今日问卷。")
            return
        
        # 查找今天的报告
        report_path = f"reports/daily_report_{today}.md"
        pdf_path = f"reports/daily_report_{today}.pdf"
        
        if os.path.exists(pdf_path):
            print(f"\n📄 今日报告: {pdf_path}")
            print("请打开文件查看详细内容")
        elif os.path.exists(report_path):
            print(f"\n📄 今日报告: {report_path}")
            print("\n报告内容预览:")
            print("-" * 50)
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                # 只显示前500个字符
                print(content[:500] + "..." if len(content) > 500 else content)
        else:
            print("\n❌ 找不到今日报告文件")
    
    def view_points_history(self):
        print("\n" + "=" * 50)
        print("📊 积分历史记录")
        print("=" * 50)
        
        # 显示积分表格
        table = self.data_manager.generate_points_table()
        print("\n最近10天记录:")
        print(table)
        
        # 显示总积分
        total_points = self.data_manager.get_total_points()
        level_info = self.scoring.get_level_info(total_points)
        
        print(f"\n💰 当前总积分: {total_points}分")
        print(f"🏆 当前等级: {level_info['current']['emoji']} {level_info['current']['name']}")
        
        if level_info['next']:
            progress_bar = self._generate_progress_bar(level_info['progress'], 
                                                      level_info['next']['min_points'] - level_info['current']['min_points'])
            print(f"📈 升级进度: {progress_bar} ({level_info['progress']}/{level_info['needed']}分)")
    
    def _generate_progress_bar(self, current: int, total: int) -> str:
        if total == 0:
            return "████████████████████ 100%"
        
        percentage = min(100, int(current / total * 100))
        filled = int(percentage / 5)  # 20个格子
        bar = "█" * filled + "░" * (20 - filled)
        return f"{bar} {percentage}%"
    
    def view_statistics(self):
        print("\n" + "=" * 50)
        print("📈 学习统计数据")
        print("=" * 50)
        
        stats = self.data_manager.get_statistics()
        
        print(f"\n📅 总学习天数: {stats['study_days']}天")
        print(f"📝 总签到天数: {stats['total_days']}天")
        print(f"💰 总积分: {stats['total_points']}分")
        print(f"📊 平均每日积分: {stats['avg_daily_points']}分")
        print(f"⏱️ 总学习时长: {stats['total_study_time']}分钟 ({stats['total_study_time']//60}小时{stats['total_study_time']%60}分钟)")
        print(f"✏️ 总做题数: {stats['total_problems']}道")
        
        if stats['study_days'] > 0:
            print(f"📖 平均每天学习: {stats['total_study_time']//stats['study_days']}分钟")
            print(f"📝 平均每天做题: {stats['total_problems']//stats['study_days']}道")
    
    def generate_weekly_summary(self):
        print("\n⏳ 正在生成周总结...")
        
        summary_path = self.report_generator.generate_weekly_summary()
        
        if summary_path:
            print(f"\n✅ 周总结已生成: {summary_path}")
        else:
            print("\n❌ 数据不足，无法生成周总结")
    
    def visualize_progress(self):
        print("\n⏳ 正在生成进度图表...")
        
        # 让用户选择时间范围
        print("\n选择时间范围:")
        print("1. 最近7天")
        print("2. 最近30天")
        print("3. 全部数据")
        
        choice = input("请选择 (默认为30天): ").strip()
        
        if choice == '1':
            days = 7
        elif choice == '3':
            days = None
        else:
            days = 30
        
        chart_path = self.data_manager.visualize_points_trend(days or 9999)
        
        if chart_path:
            print(f"\n✅ 图表已生成: {chart_path}")
        else:
            print("\n❌ 数据不足，无法生成图表")
    
    def export_data(self):
        print("\n选择导出格式:")
        print("1. JSON格式 (完整数据)")
        print("2. CSV格式 (积分历史)")
        
        choice = input("请选择: ").strip()
        
        if choice == '1':
            export_path = self.data_manager.export_data('json')
        elif choice == '2':
            export_path = self.data_manager.export_data('csv')
        else:
            print("\n❌ 无效选择")
            return
        
        print(f"\n✅ 数据已导出: {export_path}")


def main():
    diary = StudyDiary()
    
    # 显示欢迎信息
    print("\n" + "🌟" * 30)
    print("\n欢迎使用 ZZW考公学习日记系统！")
    print("\n这是你的专属学习伙伴，我会陪伴你走过考公之路。")
    print("让我们一起努力，向着目标前进！💪")
    print("\n" + "🌟" * 30)
    
    try:
        diary.run()
    except KeyboardInterrupt:
        print("\n\n👋 再见！继续加油，考公必胜！")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        print("请联系开发者解决问题")


if __name__ == "__main__":
    main()