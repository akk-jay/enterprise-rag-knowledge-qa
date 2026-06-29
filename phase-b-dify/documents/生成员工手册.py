# -*- coding: utf-8 -*-
"""Generate 员工手册.pdf — Employee Handbook for RAG knowledge base testing."""

import os
from fpdf import FPDF

# ── Paths ──────────────────────────────────────────────────────────
OUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUT_PDF = os.path.join(OUT_DIR, "员工手册.pdf")

# ── Chinese font ────────────────────────────────────────────────────
# Try common Windows Chinese fonts in order of preference.
FONT_CANDIDATES = [
    r"C:/Windows/Fonts/simhei.ttf",   # 黑体
    r"C:/Windows/Fonts/msyh.ttf",     # 微软雅黑
    r"C:/Windows/Fonts/simsun.ttc",   # 宋体
    r"C:/Windows/Fonts/simkai.ttf",   # 楷体
]
FONT_FILE = None
for path in FONT_CANDIDATES:
    if os.path.isfile(path):
        FONT_FILE = path
        break

if FONT_FILE is None:
    raise FileNotFoundError(
        "No Chinese TTF font found on this system. Tried:\n" +
        "\n".join(f"  {p}" for p in FONT_CANDIDATES)
    )


class EmployeeHandbook(FPDF):
    """PDF generator with header/footer and styled heading hierarchy."""

    def __init__(self):
        super().__init__(orientation="P", unit="mm", format="A4")
        self.set_auto_page_break(True, margin=25)
        # Register the Chinese font
        self.add_font("zh", "", FONT_FILE)
        self.add_font("zh", "B", FONT_FILE)  # same file; bold rendered via styling

    # ── Header / Footer ─────────────────────────────────────────
    def header(self):
        if self.page_no() == 1:
            return  # no header on cover page
        self.set_font("zh", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 6, "XX科技有限公司 · 员工手册 V3.2", align="L")
        self.cell(0, 6, "内部资料 · 注意保密", align="R", new_x="LMARGIN", new_y="NEXT")
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(4)

    def footer(self):
        if self.page_no() == 1:
            return
        self.set_y(-20)
        self.set_font("zh", "", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"第 {self.page_no()} 页", align="C")

    # ── Helpers ─────────────────────────────────────────────────
    def cover_page(self):
        """Draw an attractive cover page."""
        self.add_page()
        # Decorative top bar
        self.set_fill_color(30, 60, 120)
        self.rect(0, 0, 210, 8, "F")
        self.ln(55)

        # Company name
        self.set_font("zh", "B", 28)
        self.set_text_color(30, 60, 120)
        self.cell(0, 14, "XX科技有限公司", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(6)

        # Separator line
        self.set_draw_color(30, 60, 120)
        self.set_line_width(0.6)
        x_center = self.w / 2
        self.line(x_center - 30, self.get_y(), x_center + 30, self.get_y())
        self.ln(10)

        # Handbook title
        self.set_font("zh", "B", 36)
        self.set_text_color(30, 60, 120)
        self.cell(0, 16, "员工手册", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(16)

        # Meta info box
        self.set_font("zh", "", 12)
        self.set_text_color(80, 80, 80)
        meta_items = [
            ("版  本  号：", "V3.2"),
            ("生效日期：", "2025年1月1日"),
            ("编  制  部：", "人力资源部"),
            ("审  批  人：", "总经理办公会"),
            ("密      级：", "内部公开"),
        ]
        for label, value in meta_items:
            self.cell(0, 10, f"{label}    {value}", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(20)

        # Bottom bar
        self.set_fill_color(30, 60, 120)
        self.rect(0, 289, 210, 8, "F")

    def section_level1(self, title):
        """Bold 13pt heading for top-level sections (一、…)."""
        self.ln(4)
        self.set_font("zh", "B", 13)
        self.set_text_color(30, 60, 120)
        self.multi_cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        # Underline effect
        self.set_draw_color(30, 60, 120)
        self.set_line_width(0.3)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(4)

    def section_level2(self, title):
        """Bold 11pt heading for sub-sections (1.1 …)."""
        self.ln(2)
        self.set_font("zh", "B", 11)
        self.set_text_color(60, 60, 60)
        self.multi_cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        """Regular 10pt multi_cell body text."""
        self.set_font("zh", "", 10)
        self.set_text_color(40, 40, 40)
        self.multi_cell(0, 6.5, text, align="L", new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_bullet(self, text, indent=4):
        """Indented bullet-style item."""
        self.set_font("zh", "", 10)
        self.set_text_color(40, 40, 40)
        x0 = self.l_margin + indent
        self.set_x(x0)
        self.multi_cell(self.w - self.l_margin - self.r_margin - indent, 6.5,
                        text, align="L", new_x="LMARGIN", new_y="NEXT")

    # ── Table helper ─────────────────────────────────────────────
    def simple_table(self, headers, rows, col_widths=None):
        """Draw a simple table with header row."""
        if col_widths is None:
            col_widths = [self.w / len(headers)] * len(headers)
        total_w = sum(col_widths)

        # Header
        self.set_font("zh", "B", 9)
        self.set_fill_color(220, 225, 235)
        self.set_text_color(30, 30, 30)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 8, h, border=1, fill=True, align="C")
        self.ln()

        # Data rows
        self.set_font("zh", "", 9)
        self.set_text_color(40, 40, 40)
        for row in rows:
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 7.5, str(cell), border=1, align="C")
            self.ln()
        self.ln(3)


# ═══════════════════════════════════════════════════════════════════
#  BUILD DOCUMENT
# ═══════════════════════════════════════════════════════════════════

pdf = EmployeeHandbook()

# ── COVER ───────────────────────────────────────────────────────
pdf.cover_page()

# ── FOREWORD ────────────────────────────────────────────────────
pdf.add_page()
pdf.section_level1("前  言")
pdf.body_text(
    "欢迎加入XX科技有限公司！本《员工手册》依据《中华人民共和国劳动法》《中华人民共和国劳动合同法》"
    "及相关法律法规，结合本公司实际情况制定。手册旨在帮助全体员工了解公司的基本制度、权利义务及行为规范，"
    "以营造公平、透明、高效的工作环境。本手册适用于公司全体正式员工及试用期员工（另有约定的除外）。"
    "各部门、各岗位的具体操作规程，以部门发布的补充文件为准。手册由人力资源部负责解释与修订，"
    "经总经理办公会审议通过后生效。员工入职时应认真阅读本手册并签署确认书，确认已知悉并愿意遵守相关制度。"
    "手册内容如与国家法律法规发生冲突，以法律法规为准。"
)
pdf.body_text(
    "本手册为 V3.2 版，自 2025 年 1 月 1 日起施行，此前版本的员工手册同时废止。"
    "公司保留根据经营发展需要适时修订的权利，修订内容将通过企业微信、公司内网及公告栏等方式公示。"
)

# ═══════════════════════════════════════════════════════════════
#  一、考勤制度
# ═══════════════════════════════════════════════════════════════
pdf.section_level1("一、考勤制度")

# ── 1.1 工作时间 ──────────────────────────────────────────────
pdf.section_level2("1.1  工作时间")
pdf.body_text(
    "公司实行以标准工时制为主、弹性工作制为辅的考勤管理模式。"
    "标准工时制适用于公司总部及各地分公司的行政、财务、运营等后台岗位，"
    "工作时间为每周一至周五，上午 9:00 至 12:00，下午 13:00 至 18:00，"
    "每日实际工作 8 小时，周累计工作 40 小时。午休时间为 12:00 至 13:00，"
    "午休期间不计入工作时间，员工可自由支配。"
)
pdf.body_text(
    "弹性工作制适用于研发中心、产品设计部及经总经理特批的远程办公岗位。"
    "弹性工作制员工每日核心在岗时段为 10:00 至 16:00（必须到岗或在线），"
    "其余 2 小时可在 7:00 至 21:00 之间自由安排，当日总工时须达到 8 小时。"
    "采用弹性工作制的员工须提前一周向直属上级提交《弹性工时申请表》，"
    "经部门负责人及人力资源部审批后方可执行，每次审批有效期为 6 个月，"
    "到期后须重新申请。"
)

# ── 1.2 打卡规定 ──────────────────────────────────────────────
pdf.section_level2("1.2  打卡规定")
pdf.body_text(
    "全体员工（含弹性工作制员工）须通过公司指定的手机客户端（企业微信-考勤模块）"
    "进行每日打卡。标准工时制员工每日打卡 2 次：上午上班 1 次（9:00 前），"
    "下午下班 1 次（18:00 后）。弹性工作制员工每日打卡 2 次：核心时段开始时 1 次，"
    "当日离岗时 1 次。打卡须在距公司办公地点 300 米范围内完成（GPS 定位验证），"
    "远程办公人员须在打卡时上传实时定位截图。"
)
pdf.body_text(
    "如遇手机电量耗尽、网络故障、GPS 定位失败等特殊情况导致无法正常打卡的，"
    "员工应在故障发生后 30 分钟内在企业微信提交《考勤异常说明》，注明异常原因、"
    "时间及证明人（如有）。每月累计缺卡或异常打卡超过 3 次的部分，"
    "每次按迟到处理。严禁代他人打卡或使用虚拟定位工具作弊，"
    "一经查实，双方均按严重违纪处理，扣发当月全勤奖并通报批评；"
    "情节严重的，公司有权单方解除劳动合同。"
)

# ── 1.3 迟到与早退 ──────────────────────────────────────────
pdf.section_level2("1.3  迟到与早退")
pdf.body_text(
    "迟到定义为超过规定上班时间后到达岗位，早退定义为在规定下班时间前擅自离岗。"
    "具体处理标准如下："
)
pdf.body_bullet("● 迟到 30 分钟（含）以内：每次扣除当月绩效考评分 1 分，扣发当日全勤奖；")
pdf.body_bullet("● 迟到 30 分钟以上、2 小时以内：每次扣除绩效考评分 3 分，按半天事假处理；")
pdf.body_bullet("● 迟到超过 2 小时或无故缺勤：按旷工半天计算，扣除当日全部工资及当月全勤奖；")
pdf.body_bullet("● 早退 30 分钟以内：每次扣除绩效考评分 1 分；")
pdf.body_bullet("● 早退超过 30 分钟：按旷工半天处理。")
pdf.body_text(
    "每月迟到或早退累计达到 5 次，或连续 2 个月累计达到 8 次者，"
    "取消当年度评优资格，并由直属上级进行诫勉谈话。以下情况经核实属实的，"
    "可豁免迟到或早退处分：① 城市发布红色暴雨/暴雪预警导致公共交通瘫痪；"
    "② 途中遭遇交通事故且有交警出具的事故证明；③ 直系亲属突发疾病需紧急送医；"
    "④ 其他经人力资源部认定的不可抗力因素。豁免申请须在到岗后 1 个工作日内提交，"
    "过期不予受理。"
)

# ═══════════════════════════════════════════════════════════════
#  二、休假政策
# ═══════════════════════════════════════════════════════════════
pdf.section_level1("二、休假政策")

# ── 2.1 年假 ──────────────────────────────────────────────────
pdf.section_level2("2.1  年假")
pdf.body_text(
    "员工入职满 1 年后享有带薪年假。年假天数按累计工作年限分档计算，"
    "当年度年假天数 = 全年可享天数 ×（当年剩余日历天数 ÷ 365），"
    "不足 0.5 天的部分不计入。具体分档如下："
)
pdf.simple_table(
    ["累计工作年限", "年假天数", "备注"],
    [
        ["满 1 年，不足 3 年", "5 天", "入职满 1 年后方可享受"],
        ["满 3 年，不足 5 年", "10 天", "含法定年假 5 天 + 公司福利年假 5 天"],
        ["满 5 年，不足 10 年", "15 天", "含法定年假 10 天 + 公司福利年假 5 天"],
        ["满 10 年及以上", "20 天", "含法定年假 15 天 + 公司福利年假 5 天"],
    ],
    [50, 40, 100],
)
pdf.body_text(
    "年假须提前至少 5 个工作日通过 OA 系统提交申请，经直属上级和部门负责人审批。"
    "年假最小请假单位为半天（4 小时）。当年度未休完的年假可结转至下一年度，"
    "但结转天数不得超过当年度应享年假的 50%，且须在次年 3 月 31 日前休完，"
    "逾期自动作废。离职员工当年度未休年假按国家规定折算工资补偿。"
)

# ── 2.2 病假 ──────────────────────────────────────────────────
pdf.section_level2("2.2  病假")
pdf.body_text(
    "员工因病或非因工负伤需要治疗的，可申请病假。申请病假须提供二级甲等及以上医院"
    "出具的诊断证明（含建议休假天数的医嘱）和挂号/缴费凭证。急诊情况下可先口头向"
    "直属上级请假，并在到岗后 2 个工作日内补齐书面材料。"
)
pdf.body_text(
    "病假审批与待遇标准："
)
pdf.body_bullet("● 2 天（含）以内：由直属上级审批，工资按正常标准的 100% 发放；")
pdf.body_bullet("● 3 天至 15 天：经直属上级及部门负责人审批，工资按当地最低工资标准的 80% 发放；")
pdf.body_bullet("● 超过 15 天：进入医疗期管理，按《企业职工患病或非因工负伤医疗期规定》执行；")
pdf.body_bullet("● 年度累计病假超过 30 天：超出部分不发放工资，且不计入当年度年假计算工龄。")
pdf.body_text(
    "伪造病假证明或利用病假从事与治疗无关活动（如旅游、兼职等）的，"
    "一经发现按严重违纪处理。"
)

# ── 2.3 事假 ──────────────────────────────────────────────────
pdf.section_level2("2.3  事假")
pdf.body_text(
    "员工因私事无法出勤的，可申请无薪事假。事假须提前至少 1 个工作日提交申请，"
    "紧急情况（如家庭成员突发事故）可先口头报备，事后 1 个工作日内补交申请。"
    "事假最小请假单位为 1 小时，不足 1 小时的按 1 小时计算。"
)
pdf.body_text(
    "事假期间不发放工资，工资扣除公式为：日工资 = 月基本工资 ÷ 21.75 天。"
    "员工年度累计事假不得超过 20 天（含）。超过 20 天的部分，"
    "公司有权不予批准；累计超过 30 天的，公司可酌情调整岗位或安排培训。"
    "连续事假超过 5 个工作日的，须经分管副总审批。"
    "试用期员工原则上不得申请超过 3 天的连续事假。"
)

# ═══════════════════════════════════════════════════════════════
#  三、薪酬福利
# ═══════════════════════════════════════════════════════════════
pdf.section_level1("三、薪酬福利")

# ── 3.1 薪资构成 ──────────────────────────────────────────────
pdf.section_level2("3.1  薪资构成")
pdf.body_text(
    "员工月薪由以下部分构成："
)
pdf.body_bullet("① 基本工资：根据岗位职级、市场薪酬水平及个人能力综合确定，占月度总薪的 50%-60%；")
pdf.body_bullet("② 岗位津贴：根据岗位性质、工作强度及特殊技能要求发放，标准为 500-3000 元/月不等；")
pdf.body_bullet("③ 绩效工资：根据当月绩效考核结果浮动，详见 3.2 节；")
pdf.body_bullet("④ 全勤奖：当月无迟到、早退、旷工、事假、病假记录的，发放全勤奖 300 元；")
pdf.body_bullet("⑤ 加班补贴：法定工作日延长加班按 1.5 倍小时工资计算，休息日加班按 2 倍计算，法定节假日加班按 3 倍计算。")
pdf.body_text(
    "薪资发放日为每月最后一个工作日。如遇法定节假日，则提前至节前最后一个工作日发放。"
    "新入职员工当月薪资按实际出勤天数折算。离职员工最后一个月薪资在办理完离职交接手续后 5 个工作日内结清。"
    "公司依法代扣代缴个人所得税及个人承担的社会保险、住房公积金部分。"
)

# ── 3.2 绩效考核 ──────────────────────────────────────────────
pdf.section_level2("3.2  绩效考核")
pdf.body_text(
    "公司实行月度考核与年度考核相结合的双轨绩效考核体系。"
    "月度考核由直属上级根据员工当月工作目标完成度、工作质量、团队协作、"
    "学习成长四个维度进行评分，满分 100 分。月度绩效工资发放系数如下："
)
pdf.simple_table(
    ["考核等级", "分数区间", "绩效工资发放系数"],
    [
        ["S档（卓越）", "90 分及以上", "120%"],
        ["A档（优秀）", "80 - 89 分", "100%"],
        ["B档（良好）", "70 - 79 分", "80%"],
        ["C档（待改进）", "60 - 69 分", "60%"],
        ["D档（不合格）", "59 分及以下", "0%（无绩效工资）"],
    ],
    [45, 55, 90],
)
pdf.body_text(
    "年度考核综合 12 个月的月度考核结果及年度重点项目完成情况评定。"
    "年度考核等级为 S 档的员工，额外发放 2 个月基本工资作为年度绩效奖金；"
    "A 档发放 1 个月基本工资；B 档发放 0.5 个月基本工资；C 档及以下不发放年度奖金。"
    "连续两个月月度考核为 D 档，或年度考核为 D 档的员工，"
    "公司将启动绩效改进计划（PIP），给予 2 个月的改进期，"
    "改进期满仍不合格的，公司有权依法解除劳动合同。"
)

# ── 3.3 五险一金 ──────────────────────────────────────────────
pdf.section_level2("3.3  五险一金")
pdf.body_text(
    "公司依法为全体员工缴纳五险一金（养老保险、医疗保险、失业保险、工伤保险、"
    "生育保险及住房公积金）。新员工入职当月即在参保地办理社会保险登记及公积金开户，"
    "缴费基数按员工首月全额工资核定，每年 7 月根据上年度月平均工资统一调整。"
    "个人缴费部分由公司在每月工资中代扣代缴。"
)
pdf.body_text(
    "公司额外为全体员工购买补充商业保险，包括：① 团体意外伤害保险（保额 30 万元/人/年）；"
    "② 补充医疗保险（门诊及住院费用在社保报销后额外报销 80%，年度上限 2 万元）；"
    "③ 定期寿险（保额 10 万元/人）。商业保险自员工转正之日起生效，"
    "离职当日自动终止。具体保险条款以保险公司签发的正式保单为准。"
)

# ═══════════════════════════════════════════════════════════════
#  四、行为规范
# ═══════════════════════════════════════════════════════════════
pdf.section_level1("四、行为规范")

# ── 4.1 办公纪律 ──────────────────────────────────────────────
pdf.section_level2("4.1  办公纪律")
pdf.body_text(
    "全体员工应自觉维护良好的办公秩序和环境。具体规定如下："
)
pdf.body_bullet("● 工作时间禁止在办公电脑上玩游戏、观看视频、进行与工作无关的网络购物或社交媒体浏览；")
pdf.body_bullet("● 办公区域应保持安静，接打电话时注意控制音量，长时间讨论请移步会议室或休闲区；")
pdf.body_bullet("● 个人工位应保持整洁，下班前清理桌面，不得在工位堆放杂物或易燃物品；")
pdf.body_bullet("● 使用会议室须提前通过 OA 系统预约，会议结束后应恢复桌椅摆放、擦除白板、关闭投影设备及电源；")
pdf.body_bullet("● 公司全域（含卫生间、走廊、楼梯间）禁止吸烟，违者每次罚款 100 元并通报批评；")
pdf.body_bullet("● 公共打印机/饮水机/微波炉等设施用后应及时清理，不得长时间占用。")
pdf.body_text(
    "违反办公纪律的，首次由直属上级口头提醒；二次由部门负责人书面警告；"
    "三次及以上纳入月度绩效考核扣分项，每项每次扣 2 分。"
    "在办公区域饮酒、赌博、打架斗殴或进行其他违法违纪活动的，"
    "公司有权立即解除劳动合同并移交司法机关处理。"
)

# ── 4.2 着装要求 ──────────────────────────────────────────────
pdf.section_level2("4.2  着装要求")
pdf.body_text(
    "公司日常办公执行商务休闲（Business Casual）着装标准。具体规定如下："
)
pdf.body_bullet("● 周一至周四：男士可穿着长裤/卡其裤搭配有领衬衫或 Polo 衫，女士可穿着得体裙装/裤装——禁止穿着拖鞋、凉拖、背心、运动短裤、超短裙（裙摆高于膝上 10cm）及带有不雅图案/文字的服装；")
pdf.body_bullet("● 周五为便装日（Casual Friday）：员工可穿着整洁的便装，但不得穿着拖鞋、睡衣类服装或过度暴露的服饰；")
pdf.body_bullet("● 对外商务接待、客户拜访、政府对接等正式场合，无论日期均须着正装（男士西装领带、女士职业套装）；")
pdf.body_bullet("● 实验室、机房、仓库等特殊作业区域，须按安全规程穿戴规定的防护用品（如防静电服、安全帽、防护鞋等）。")
pdf.body_text(
    "违反着装规定的，每次扣当月绩效考评分 0.5 分。"
    "对外活动因着装不当造成不良影响的，按严重违纪处理。"
)

# ── 4.3 信息安全 ──────────────────────────────────────────────
pdf.section_level2("4.3  信息安全")
pdf.body_text(
    "保护公司信息安全是每一位员工的法定义务和职业操守要求。核心规定如下："
)
pdf.body_bullet("● 未经授权，不得向任何第三方（含已离职同事、媒体、竞品公司）泄露公司未公开的经营数据、客户信息、技术文档、产品规划、财务报告及内部决策信息；")
pdf.body_bullet("● 员工离开工位时应立即锁定计算机屏幕（Windows 快捷键 Win+L，macOS 快捷键 Control+Command+Q），超过 5 分钟不归位的，稽查人员有权记录并通报；")
pdf.body_bullet("● 严禁使用个人电子邮箱（如 QQ 邮箱、163 邮箱、Gmail 等）、个人网盘或即时通讯工具传输涉密工作文件，所有工作文件传输须使用公司企业邮箱及经批准的协同办公平台；")
pdf.body_bullet("● 外部人员来访须在前台登记并全程由接待人员陪同，不得在办公区域随意拍照或录像；")
pdf.body_bullet("● 离职员工须在离职日期前完成全部公司资料、设备、门禁卡及系统账号的归还与注销，由 IT 部门确认后人力资源部方可办理离职证明。")
pdf.body_text(
    "违反信息安全规定尚未造成损失的，给予书面警告并扣发当月全部绩效工资；"
    "造成损失的，依法追究赔偿责任；情节严重的，依法追究刑事责任并移交公安机关。"
    "公司保留对违反保密义务的前员工追究法律责任的权利，包括但不限于提起民事诉讼。"
)

# ── 结语 ────────────────────────────────────────────────────
pdf.section_level1("结  语")
pdf.body_text(
    "本手册是公司管理制度体系的重要组成部分，每一位员工都应认真学习并严格遵守。"
    "良好的制度需要全体同仁的共同维护与践行。希望各位员工以主人翁精神投入工作，"
    "在实现个人职业发展的同时，与公司共同成长、共创未来。"
)
pdf.body_text(
    "如对本手册内容有任何疑问，或在实际工作中遇到手册未覆盖的特殊情况，"
    "欢迎向直属上级或人力资源部咨询。我们将持续倾听员工的声音，"
    "不断优化和完善公司的管理体系。"
)
pdf.body_text("XX科技有限公司  人力资源部")
pdf.body_text("2025 年 1 月 1 日")

# ── SAVE ───────────────────────────────────────────────────────
pdf.output(OUT_PDF)
print(f"PDF generated successfully: {OUT_PDF}")
print(f"File size: {os.path.getsize(OUT_PDF):,} bytes")
print(f"Total pages: {pdf.page_no()}")
