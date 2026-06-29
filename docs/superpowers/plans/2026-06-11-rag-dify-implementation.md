# Phase B: Dify RAG 知识库 - 实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 在 Dify 平台搭建完整的 RAG 知识库问答系统，含 5 份模拟企业文档、Prompt 模板、工作流编排和测试验证。

**Architecture:** 内容生成（Python 脚本写文档）→ Dify 配置（Web UI 手动操作）→ 测试验证（10 题问答 + 准确率统计）

**Tech Stack:** Python (fpdf2, python-docx), Dify Docker, Weaviate, 国内大模型 API

---

### File Structure Map

```
企业问答知识库/
├── README.md                                  # CREATE - 项目说明
├── phase-b-dify/
│   ├── documents/
│   │   ├── 员工手册.py                         # CREATE - 生成 PDF 的脚本
│   │   ├── IT安全管理制度.py                    # CREATE - 生成 PDF 的脚本
│   │   ├── 产品手册-云办公平台.py                # CREATE - 生成 DOCX 的脚本
│   │   ├── 财务报销制度.py                      # CREATE - 生成 DOCX 的脚本
│   │   └── 新员工入职指南.txt                   # CREATE - 直接写 TXT
│   ├── prompts/
│   │   ├── system-prompt.md                   # CREATE - 系统提示词
│   │   └── user-prompt.md                     # CREATE - 用户提示词模板
│   ├── test-questions.md                      # CREATE - 10 个测试问题
│   ├── dify-workflow-config.md                # CREATE - 工作流配置记录
│   └── test-results.md                        # CREATE - 测试结果记录
├── notes/
│   └── rag-notes.md                           # CREATE - 学习笔记模板
└── docs/superpowers/specs/
    └── 2026-06-11-rag-knowledge-base-design.md # DONE - 设计方案
```

每个文档生成脚本的结构相同：
1. 定义文档内容（中文字符串）
2. 调用库函数生成文件
3. 输出到 `documents/` 目录

---

### Task 1: 项目 README

**Files:**
- Create: `README.md`

- [ ] **Step 1: 编写 README.md**

```markdown
# 企业文档知识库问答 Agent

基于 RAG（检索增强生成）技术的企业级文档知识库问答系统。

## 项目结构

- `phase-b-dify/` - Dify 平台实现（RAG 工作流）
- `phase-a-scratch/` - 手写代码实现（后续）
- `notes/` - 学习笔记

## 快速开始

### 环境要求
- Docker + Dify
- Python 3.x
- 国内大模型 API Key（DeepSeek / 通义千问）

### 阶段 B：Dify 平台

1. 启动 Dify：`docker compose up -d`（在 dify/docker 目录）
2. 访问 http://localhost
3. 将 `phase-b-dify/documents/` 下的文档上传至 Dify 知识库
4. 按 `phase-b-dify/dify-workflow-config.md` 配置工作流
5. 使用 `phase-b-dify/test-questions.md` 验证效果

### 阶段 A：手写实现（待开发）

Python + FastAPI + Chroma 从零实现 RAG。
```

- [ ] **Step 2: 写入文件**

Write 到 `README.md`

---

### Task 2: 生成《员工手册》PDF

**Files:**
- Create: `phase-b-dify/documents/生成员工手册.py`（执行后生成 `员工手册.pdf`）

文档内容结构：
```
一、考勤制度
  1.1 工作时间
  1.2 打卡规定
  1.3 迟到与早退
二、休假政策
  2.1 年假
  2.2 病假
  2.3 事假
三、薪酬福利
  3.1 薪资构成
  3.2 绩效考核
  3.3 五险一金
四、行为规范
  4.1 办公纪律
  4.2 着装要求
  4.3 信息安全
```

- [ ] **Step 1: 安装 fpdf2**

```bash
pip install fpdf2
```

- [ ] **Step 2: 编写 PDF 生成脚本**

```python
from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "XX科技有限公司 - 员工手册", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(5)
    
    def add_title(self, title, level=1):
        if level == 1:
            self.set_font("Helvetica", "B", 13)
            self.ln(3)
        else:
            self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
    
    def add_body(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

def generate():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    # === 封面 ===
    pdf.ln(40)
    pdf.set_font("Helvetica", "B", 24)
    pdf.cell(0, 15, "XX科技有限公司", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 12, "员 工 手 册", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 8, "版本：V3.2  |  生效日期：2025年1月1日  |  适用范围：全体员工", align="C", new_x="LMARGIN", new_y="NEXT")
    
    # === 正文 ===
    pdf.add_page()
    
    pdf.add_title("一、考勤制度")
    
    pdf.add_title("1.1 工作时间", level=2)
    pdf.add_body("公司实行标准工时制。周一至周五为工作日，工作时间为上午 9:00 至 12:00，下午 13:00 至 18:00，每日工作 8 小时。周六、周日为休息日，全体员工享有双休。研发部门可根据项目需要申请弹性工作制，经部门经理和人事总监审批后生效，弹性工作制员工核心在岗时间为上午 10:00 至下午 16:00，其余时间可自由安排。")
    
    pdf.add_title("1.2 打卡规定", level=2)
    pdf.add_body("全体员工须通过"XX办公"手机客户端或公司门禁系统进行上下班打卡。每日需打卡 2 次：上班打卡（9:00 前）和下班打卡（18:00 后）。未按时打卡视为考勤异常，须在 3 个工作日内通过 OA 系统提交考勤异常说明，经直属上级审批后由人事部门修正。连续 3 天或月度累计 5 次未打卡且未提交说明者，按旷工处理。")
    
    pdf.add_title("1.3 迟到与早退", level=2)
    pdf.add_body("员工迟到 30 分钟以内（含 30 分钟），扣除当月绩效分 1 分。迟到超过 30 分钟不足 2 小时，扣除当月绩效分 3 分，并按实际迟到时间扣除相应工资。迟到超过 2 小时按旷工半天处理。早退处罚标准与迟到相同。月度累计迟到超过 5 次或旷工超过 2 天者，取消当月全勤奖及年度评优资格，情节严重者予以警告处分。员工因不可抗力（如极端天气、交通事故等）导致迟到，可凭相关证明申请豁免，经直属上级审批后免于处罚。")
    
    pdf.add_title("二、休假政策")
    
    pdf.add_title("2.1 年假", level=2)
    pdf.add_body("员工入职满 1 年享有 5 天带薪年假；入职满 3 年享有 10 天带薪年假；入职满 5 年享有 15 天带薪年假；入职满 10 年及以上享有 20 天带薪年假。年假须在当年度内使用完毕，最多可顺延 5 天至次年 3 月 31 日前使用，逾期未休视为自动放弃，公司不另行补偿。年假申请需提前至少 5 个工作日通过 OA 系统提交，注明休假起止日期和紧急联系人，经直属上级审批后方可休假。连续休假超过 3 天须提前 2 周申请。")
    
    pdf.add_title("2.2 病假", level=2)
    pdf.add_body("员工因病需就医或休养，可申请病假。病假须提供二级甲等及以上医院出具的诊断证明或病假条。病假在 2 天以内可由直属上级审批；病假超过 2 天须报人事部门备案。月度累计病假不超过 3 天者工资照常发放；超出 3 天部分按当地最低工资标准的 80% 发放病假工资。员工因重大疾病需长期治疗者，经人事部门审核后可申请医疗期，医疗期管理按照《企业职工患病或非因工负伤医疗期规定》执行。")
    
    pdf.add_title("2.3 事假", level=2)
    pdf.add_body("员工因私事需在工作日请假，可申请事假。事假须提前至少 1 个工作日通过 OA 系统提交申请，并注明事由。事假期间不发放工资，按实际请假天数从当月薪资中扣除。年度累计事假不得超过 20 天，超出部分不予批准（特殊情况由部门经理和人事总监会签审批）。试用期员工原则上不建议请事假，如有特殊情况须经人事部门审核。")
    
    pdf.add_title("三、薪酬福利")
    
    pdf.add_title("3.1 薪资构成", level=2)
    pdf.add_body("员工薪资由以下部分构成：基本工资（占总薪资的 60%-70%）、岗位津贴（根据职级和岗位确定）、绩效工资（占总薪资的 20%-30%，与月度考核结果挂钩）、全勤奖（月度全勤奖励 300 元）、加班补贴（工作日加班按小时工资的 1.5 倍计算，休息日加班按 2 倍计算，法定节假日加班按 3 倍计算）。薪资发放日期为每月最后一个工作日，遇节假日提前至最近的工作日发放，由财务部统一转账至员工指定银行账户。")
    
    pdf.add_title("3.2 绩效考核", level=2)
    pdf.add_body("公司实行月度 + 年度两级绩效考核制度。月度考核于每月最后一周进行，由直属上级根据工作目标完成度、工作质量、团队协作三个维度评分，总分 100 分。月度考核分数直接影响当月绩效工资：90 分及以上绩效工资按 120% 发放，80-89 分按 100% 发放，70-79 分按 80% 发放，60-69 分按 60% 发放，60 分以下不发放绩效工资。年度考核综合 12 个月成绩评定 S/A/B/C/D 五档，A 档及以上有资格参与年度调薪和晋升评审，S 档额外奖励相当于 2 个月基本工资的年度奖金。")
    
    pdf.add_title("3.3 五险一金", level=2)
    pdf.add_body("公司依法为全体员工缴纳五险一金，包括养老保险、医疗保险、失业保险、工伤保险、生育保险和住房公积金。缴纳基数按照员工上一年度月平均工资确定，比例按照当地社保局和公积金管理中心最新政策执行。新员工入职当月即办理社保和公积金登记，由人事部门在入职手续办理时统一安排。员工可通过"XX市社保局"APP 或公司人事系统查询个人缴纳明细。")
    
    pdf.add_title("四、行为规范")
    
    pdf.add_title("4.1 办公纪律", level=2)
    pdf.add_body("员工在工作时间内应保持专注，不得从事与工作无关的活动（包括但不限于玩游戏、观看娱乐视频、进行个人兼职业务等）。办公区域应保持安静整洁，不得大声喧哗影响他人工作。会议室使用后须恢复桌椅摆放并关闭投影设备。个人手机在工作时间建议调至静音或震动模式，接听私人电话请移步至茶水间或走廊区域。在办公区域内严禁吸烟，吸烟请至指定吸烟区。员工应爱护公司公共财物，不得擅自挪用或带离办公设备。")
    
    pdf.add_title("4.2 着装要求", level=2)
    pdf.add_body("公司实行商务休闲着装规范。周一至周四建议着装整洁得体，不得穿拖鞋、背心、运动短裤；周五为便装日，可穿着休闲服饰，但仍需保持整洁。对外接待客户或参加正式会议时，须着正装出席。研发部门员工在非对外接待日可适当放宽着装要求，但不得影响公司形象。行政部将不定期进行着装检查，不符合要求者需立即整改。")
    
    pdf.add_title("4.3 信息安全", level=2)
    pdf.add_body("全体员工须遵守公司信息安全管理制度。不得在社交媒体、公共论坛等公开渠道泄露公司任何未公开信息（包括但不限于产品规划、财务报表、客户数据、内部邮件等）。离开座位时须锁定电脑屏幕。不得使用私人邮箱发送工作文件。公司文件不得私自拷贝至个人存储设备，因工作需要携带文件外出须经部门经理审批。员工离职时须将所持有的全部公司资料、账号权限交还至 IT 部门和人事部门。违反信息安全规定者，依据情节严重程度给予警告、罚款直至解除劳动合同的处分，造成公司损失的依法追究赔偿责任。")
    
    # === 输出 ===
    output_path = os.path.join(os.path.dirname(__file__), "员工手册.pdf")
    pdf.output(output_path)
    print(f"已生成：{output_path}")

if __name__ == "__main__":
    generate()
```

- [ ] **Step 3: 运行脚本生成 PDF**

```bash
cd "C:\Users\29542\Desktop\企业问答知识库\phase-b-dify\documents" && python 生成员工手册.py
```

- [ ] **Step 4: 验证文件存在**

```bash
ls -la "C:\Users\29542\Desktop\企业问答知识库\phase-b-dify\documents\员工手册.pdf"
```

---

### Task 3: 生成《IT 安全管理制度》PDF

**Files:**
- Create: `phase-b-dify/documents/生成IT安全管理制度.py`

- [ ] **Step 1: 编写脚本**

```python
from fpdf import FPDF
import os

class PDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.cell(0, 6, "XX科技有限公司 - IT安全管理制度 - 内部资料", align="C", new_x="LMARGIN", new_y="NEXT")
            self.ln(3)
    
    def add_title(self, title, level=1):
        if level == 1:
            self.set_font("Helvetica", "B", 13)
            self.ln(4)
        else:
            self.set_font("Helvetica", "B", 11)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)
    
    def add_body(self, text):
        self.set_font("Helvetica", "", 10)
        self.multi_cell(0, 6, text)
        self.ln(2)

def generate():
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    
    pdf.ln(30)
    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 15, "XX科技有限公司", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "IT 安全管理制度", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 8, "密级：内部  |  版本：V2.1  |  生效日期：2025年3月1日", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 8, "制定部门：信息技术部  |  审批人：CTO 张三", align="C", new_x="LMARGIN", new_y="NEXT")
    
    pdf.add_page()
    
    pdf.add_title("一、总则")
    pdf.add_body("为保障公司信息系统安全稳定运行，保护公司核心数据和知识产权，规范员工使用 IT 资源的行为，特制定本制度。本制度适用于公司全体员工（含正式员工、实习生、外包人员及第三方驻场人员）。信息技术部为本制度的执行和监督部门，拥有对公司所有 IT 资源的最终管理权限。违反本制度者，视情节严重程度给予通报批评、罚款、降级直至解除劳动合同的处分；触犯法律法规的，移交司法机关处理。")
    
    pdf.add_title("二、账号与密码管理")
    
    pdf.add_title("2.1 账号管理", level=2)
    pdf.add_body("每位员工入职当日由 IT 部门分配唯一工作账号，账号命名规则为：姓名全拼@公司域名。账号仅限本人使用，严禁转借、共用或借用他人账号。员工离职时，IT 部门在收到人事部门通知后 2 小时内注销其所有账号权限。各部门每季度须配合 IT 部门完成账号权限审计，清理不再需要的账号和权限。员工调岗时，原岗位权限应在调动生效当日注销，新岗位权限由新部门主管申请开通。")
    
    pdf.add_title("2.2 密码策略", level=2)
    pdf.add_body("所有系统密码须满足以下复杂度要求：长度不少于 12 个字符，必须包含大写字母、小写字母、数字和特殊符号中至少三类。密码不得包含用户名、生日、手机号等个人公开信息，不得使用常见弱密码（如 Password123、Admin@123 等）。密码有效期为 90 天，到期系统将强制要求更换，新密码不得与过去 5 次使用过的密码重复。连续输错密码 5 次将触发账号锁定 30 分钟，联系 IT 部门值班电话可紧急解锁。员工遗忘密码可通过企业微信自助重置流程完成密码重置，需验证手机验证码和人脸识别。严禁将密码写在便签上、贴在显示器上或以任何明文形式保存。")
    
    pdf.add_title("三、数据安全")
    
    pdf.add_title("3.1 数据分类", level=2)
    pdf.add_body("公司数据分为三个安全等级：公开级（对外可公开的市场资料、产品白皮书等）、内部级（仅供公司内部使用的制度规范、会议纪要、技术文档等）和机密级（涉及商业机密的核心数据：源代码、客户合同、财务报表、未发布的产品规划等）。公开级数据可通过公司官网、公众号等渠道对外发布；内部级数据不得发送至公司外部邮箱或存储至个人云盘；机密级数据须存储在加密分区内，访问需申请权限并由部门总监审批，操作日志保留不少于 180 天。")
    
    pdf.add_title("3.2 数据备份", level=2)
    pdf.add_body("公司核心业务系统实行每日自动备份机制：数据库每日凌晨 2:00 执行全量备份，备份文件异地存储至公司灾备中心。关键业务服务器每周日凌晨 3:00 执行系统级快照备份。文件服务器每日增量备份 + 每周全量备份，备份数据保留策略为：近 7 天每日保留、近 4 周每周保留、近 12 个月每月保留。员工个人工作文件应统一存储至公司文件服务器（网络驱动器 Z:盘）或协作云平台，本地电脑硬盘中的数据由个人自行负责备份。IT 部门每季度组织一次数据恢复演练，验证备份数据可用性和恢复流程的有效性。")
    
    pdf.add_title("四、网络安全")
    
    pdf.add_title("4.1 VPN 使用规范", level=2)
    pdf.add_body("远程办公或出差员工可通过公司 VPN 安全接入公司内网。VPN 客户端下载地址为公司内部软件中心（http://soft.公司域名.com），安装后使用工作账号和密码登录。VPN 连接仅在需要访问公司内网资源时（如文件服务器、OA 系统、代码仓库等）启用，使用完毕后应及时断开，不得长期保持连接。严禁将 VPN 账号提供给非公司人员使用，严禁通过 VPN 从事与工作无关的网络活动（如访问非法网站、P2P 下载等）。VPN 使用日志由 IT 部门保留 90 天，定期审计异常登录行为。移动设备连接 VPN 须先安装公司指定的移动设备管理软件（MDM），确保设备符合安全基线要求。")
    
    pdf.add_title("4.2 邮件安全", level=2)
    pdf.add_body("员工应使用公司企业邮箱（@公司域名.com）进行工作沟通，严禁使用个人邮箱（QQ邮箱、163邮箱等）发送工作相关邮件。收到外部陌生发件人的邮件时，勿轻易点击链接或下载附件，应首先核实发件人身份。对于涉及付款、合同变更等敏感事项的邮件，须通过电话或当面二次确认。带有"外部邮件"标记的邮件来自公司外部，处理时须格外谨慎。当发现可疑邮件或疑似钓鱼邮件时，应立即通过 Outlook 的"报告钓鱼邮件"按钮上报至 IT 安全团队，不得自行转发或回复。IT 部门每月组织一次钓鱼邮件模拟演练，未通过测试的员工须参加信息安全再培训。")
    
    pdf.add_title("五、设备管理")
    
    pdf.add_body("公司配发的电脑、显示器、打印机等 IT 设备属于公司资产，员工领用时须在资产管理系统登记。公司电脑默认安装加密软件和终端安全管理软件，员工不得卸载或禁用。个人设备（含手机、平板、个人笔记本电脑等）不得接入公司有线网络，可通过访客 Wi-Fi 访问互联网。设备出现故障应联系 IT 部门处理，不得自行拆卸或送外维修。员工离职时须归还全部公司 IT 设备，IT 部门确认设备完好后签署资产归还确认书。设备丢失或被盗应立即向 IT 部门和行政部报告，IT 部门将远程擦除设备数据。")
    
    pdf.add_title("六、违规处理")
    
    pdf.add_body("违反本制度相关条款，未造成实际损失的，给予口头警告并限期整改；两次以上违规者进行全公司通报批评。因违规操作导致公司数据泄露或信息系统受损的，根据损失程度给予罚款（500-50000 元）、降级或解除劳动合同，并保留追究法律责任的权利。故意泄露公司机密数据、利用公司 IT 资源从事违法犯罪活动的，立即解除劳动合同并移交公安机关处理。各部门主管对本部门员工的信息安全行为负有管理责任，部门发生重大信息安全事件时，部门主管承担连带管理责任。")
    
    output_path = os.path.join(os.path.dirname(__file__), "IT安全管理制度.pdf")
    pdf.output(output_path)
    print(f"已生成：{output_path}")

if __name__ == "__main__":
    generate()
```

- [ ] **Step 2: 运行脚本**

```bash
cd "C:\Users\29542\Desktop\企业问答知识库\phase-b-dify\documents" && python 生成IT安全管理制度.py
```

- [ ] **Step 3: 验证文件存在**

```bash
ls -la "C:\Users\29542\Desktop\企业问答知识库\phase-b-dify\documents\IT安全管理制度.pdf"
```

---

### Task 4: 生成《产品手册 - 云办公平台》DOCX

**Files:**
- Create: `phase-b-dify/documents/生成产品手册.py`

- [ ] **Step 1: 编写脚本**

```python
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def add_heading_styled(doc, text, level):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x56, 0xDB)  # 蓝色主题
    return heading

def add_body(doc, text):
    p = doc.add_paragraph(text)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        run.font.size = Pt(10.5)
    return p

def generate():
    doc = Document()
    
    # 页面设置
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    
    # === 封面 ===
    for _ in range(6):
        doc.add_paragraph("")
    
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("云办公平台 CloudWork")
    run.font.size = Pt(28)
    run.font.bold = True
    run.font.color.rgb = RGBColor(0x1A, 0x56, 0xDB)
    
    subtitle = doc.add_paragraph()
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = subtitle.add_run("产 品 手 册")
    run.font.size = Pt(20)
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    
    doc.add_paragraph("")
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info.add_run("版本：V3.5  |  文档密级：内部  |  更新日期：2025年6月")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    
    doc.add_page_break()
    
    # === 目录页 ===
    add_heading_styled(doc, "目录", 1)
    toc_items = [
        "一、产品概述",
        "二、核心功能",
        "    2.1 即时通讯",
        "    2.2 视频会议",
        "    2.3 任务管理",
        "    2.4 文档协作",
        "    2.5 日程管理",
        "三、快速入门",
        "    3.1 创建团队",
        "    3.2 邀请成员",
        "    3.3 创建项目",
        "四、常见问题",
    ]
    for item in toc_items:
        add_body(doc, item)
    
    doc.add_page_break()
    
    # === 正文 ===
    add_heading_styled(doc, "一、产品概述", 1)
    add_body(doc, "云办公平台 CloudWork 是 XX 科技自主研发的新一代企业协同办公平台，深度融合即时通讯、视频会议、任务管理、文档协作和日程管理五大核心模块，为企业提供一站式数字化办公解决方案。平台支持 Windows、macOS、Linux 桌面端，iOS 和 Android 移动端，以及 Web 浏览器端全平台覆盖，数据实时同步。自 2023 年上线以来，已服务超过 5000 家企业客户，日活跃用户超过 50 万。平台采用微服务架构，支持私有化部署和 SaaS 两种模式，数据传输全程采用 AES-256 加密，已通过 ISO 27001 信息安全管理体系认证和等保三级测评。")
    
    add_heading_styled(doc, "二、核心功能", 1)
    
    add_heading_styled(doc, "2.1 即时通讯", 2)
    add_body(doc, "支持单聊和群聊两种模式，群聊人数上限为 5000 人。消息类型支持文字、图片、语音、视频、文件、位置分享和代码片段等。重要消息可通过"公告"功能置顶显示，确保全员知晓。消息支持撤回（发送后 5 分钟内可撤回）、已读回执、消息引用回复和多选转发。聊天记录支持关键词搜索，可按时间范围、发送人、消息类型筛选。所有消息默认采用端到端加密传输，敏感部门（如财务、法务）可开启加密模式，消息内容在服务器端也不可读。")
    
    add_heading_styled(doc, "2.2 视频会议", 2)
    add_body(doc, "支持高清视频会议，最多同时容纳 500 人参会。提供屏幕共享、白板协作、虚拟背景、美颜滤镜等功能。会议主持人可进行全员静音、锁定会议、设置等候室、录制会议等操作。会议录制文件自动保存至云端，30 天内可随时回看和下载，到期前系统自动提醒。支持与 Outlook 日历集成，预约会议时自动检测参会者忙闲状态。会议中提供实时字幕功能（支持中英文），AI 会议纪要功能可在会议结束后 5 分钟内自动生成会议纪要和待办事项列表。")
    
    add_heading_styled(doc, "2.3 任务管理", 2)
    add_body(doc, "支持创建项目、任务、子任务三级任务结构。任务可设置负责人、参与人、起止时间、优先级（紧急/高/中/低）、标签和自定义字段。提供看板视图、列表视图、甘特图视图和时间线视图四种可视化方式，满足不同管理需求。任务支持评论讨论、文件附件和进度追踪。项目管理员可设置任务依赖关系，系统自动检测关键路径和延期风险，提前 3 天向相关责任人发送提醒通知。支持从 Excel 和 Project 文件批量导入任务，也支持将项目数据导出为 Excel、PDF 格式。")
    
    add_heading_styled(doc, "2.4 文档协作", 2)
    add_body(doc, "支持多人实时在线编辑文档、表格和演示文稿，编辑历史自动保存，可随时回退至历史版本。文档支持富文本格式编辑，包括但不限于标题样式、表格、图片、代码块、数学公式等。支持通过 @提及方式在文档中添加评注，被提及者将收到消息通知。文档支持三级权限控制：仅查看、可评论、可编辑，权限可精确到每位成员或部门。所有文档自动存入知识库，支持全文搜索和标签分类管理。外部协作场景下，可生成带密码和有效期的分享链接。")
    
    add_heading_styled(doc, "2.5 日程管理", 2)
    add_body(doc, "个人日程支持创建日程、设置提醒（支持提前 5 分钟/15 分钟/30 分钟/1 小时/1 天提醒）和重复日程设置。团队日程可在日历中查看同事忙闲状态，预约会议时自动规避冲突时段。支持订阅外部日历（如 Google Calendar、Outlook Calendar），实现多渠道日程汇总显示。日程可关联相关文档和任务，创建会议日程时自动生成会议群聊。移动端支持语音创建日程，说出时间和事项即可快速添加。")
    
    add_heading_styled(doc, "三、快速入门", 1)
    
    add_heading_styled(doc, "3.1 创建团队", 2)
    add_body(doc, "注册 CloudWork 账号后，点击左侧导航栏"+"按钮，选择"创建团队"。输入团队名称（建议使用部门名称，如"产品研发部"），选择团队类型（部门/项目组/跨部门协作组），上传团队头像，点击"完成创建"。每个账号最多可创建 5 个团队。创建团队的用户默认为团队管理员，可在团队设置中将管理员权限转让给其他成员。团队管理员拥有成员管理、权限设置和团队解散等管理权限。")
    
    add_heading_styled(doc, "3.2 邀请成员", 2)
    add_body(doc, "进入团队后，点击右上角"邀请成员"按钮，可通过以下四种方式邀请：① 直接搜索公司通讯录中的同事姓名或拼音，勾选后批量邀请；② 复制团队邀请链接，通过微信、邮件等方式发送给被邀请人；③ 分享团队二维码，被邀请人使用 CloudWork 扫描二维码加入；④ 批量导入成员名单（支持 Excel 模板），适用于大批量成员导入场景。新成员加入后，系统将在团队聊天中自动发送欢迎消息，并引导新成员完成团队基础设置。")
    
    add_heading_styled(doc, "3.3 创建项目", 2)
    add_body(doc, "在团队首页点击"+"按钮，选择"新建项目"。输入项目名称、项目描述、项目起止日期，选择项目模板（空白模板/敏捷开发/营销活动/通用项目管理），点击"创建"。项目创建后，可在项目中添加任务：点击"+ 添加任务"，输入任务标题，设置执行者和截止日期，按 Enter 键快速创建。可通过鼠标拖拽调整任务顺序和优先级。项目管理员可在"项目设置"中配置任务状态流程、自定义字段、通知规则和自动化规则。")
    
    add_heading_styled(doc, "四、常见问题", 1)
    add_body(doc, "Q：CloudWork 是否支持私有化部署？\nA：支持。CloudWork 提供标准 SaaS 版和企业私有化部署版两种选择。私有化部署适用于对数据安全有较高要求的企业客户（如金融、政务、军工行业），可部署在企业自有服务器或指定云主机上。私有化部署请联系销售团队获取报价和部署方案。\n\nQ：免费版有哪些限制？\nA：免费版支持最多 50 人使用，提供基础即时通讯、文档协作和任务管理功能。视频会议单次时长上限为 45 分钟，云存储空间为每人 5GB。付费企业版无用户数限制，视频会议时长上限为 24 小时，存储空间可弹性扩容。付费方案起价为每人每月 29 元，年付享 8 折优惠。\n\nQ：数据安全性如何保障？\nA：CloudWork 已通过 ISO 27001 和等保三级认证。数据传输全程使用 TLS 1.3 加密，存储数据使用 AES-256 加密。系统每日自动备份数据至异地灾备中心，RTO（恢复时间目标）不超过 1 小时，RPO（恢复点目标）不超过 5 分钟。每年聘请第三方安全机构进行渗透测试和安全审计。\n\nQ：如何联系技术支持？\nA：工作日 9:00-18:00 可通过在线客服、服务热线 400-XXX-XXXX 或企业微信联系技术支持团队。7x24 小时紧急问题可通过值班电话联系。企业版客户配备专属客户成功经理，提供一对一服务。")
    
    output_path = os.path.join(os.path.dirname(__file__), "产品手册-云办公平台.docx")
    doc.save(output_path)
    print(f"已生成：{output_path}")

if __name__ == "__main__":
    generate()
```

- [ ] **Step 2: 运行脚本**

```bash
cd "C:\Users\29542\Desktop\企业问答知识库\phase-b-dify\documents" && python 生成产品手册.py
```

- [ ] **Step 3: 验证文件存在**

```bash
ls -la "C:\Users\29542\Desktop\企业问答知识库\phase-b-dify\documents\产品手册-云办公平台.docx"
```

---

### Task 5: 生成《财务报销制度》DOCX

**Files:**
- Create: `phase-b-dify/documents/生成财务报销制度.py`

- [ ] **Step 1: 编写脚本**

```python
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import os

def add_heading_styled(doc, text, level):
    heading = doc.add_heading(text, level=level)
    for run in heading.runs:
        run.font.color.rgb = RGBColor(0x1A, 0x56, 0xDB)
    return heading

def add_body(doc, text):
    p = doc.add_paragraph(text)
    p.paragraph_format.line_spacing = 1.5
    p.paragraph_format.space_after = Pt(6)
    for run in p.runs:
        run.font.size = Pt(10.5)
    return p

def generate():
    doc = Document()
    
    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)
    section.left_margin = Cm(2.5)
    section.right_margin = Cm(2.5)
    
    # 封面
    for _ in range(8):
        doc.add_paragraph("")
    
    title = doc.add_paragraph()
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title.add_run("XX科技有限公司")
    run.font.size = Pt(22)
    run.font.bold = True
    
    title2 = doc.add_paragraph()
    title2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = title2.add_run("财务报销制度")
    run.font.size = Pt(18)
    
    doc.add_paragraph("")
    info = doc.add_paragraph()
    info.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = info.add_run("版本：V4.0  |  生效日期：2025年1月1日  |  制定部门：财务部")
    run.font.size = Pt(9)
    run.font.color.rgb = RGBColor(0x99, 0x99, 0x99)
    
    doc.add_page_break()
    
    add_heading_styled(doc, "一、总则", 1)
    add_body(doc, "为规范公司财务报销管理，合理控制费用支出，提高资金使用效率，依据国家相关法律法规和公司财务管理制度，制定本制度。本制度适用于公司全体员工（含正式员工、试用期员工和实习生）。所有报销须遵循"事前审批、事中控制、事后报销"的原则，费用须真实发生、票据合法有效、审批流程完整。财务部为公司费用报销的归口管理部门，负责报销单据审核、费用标准核定和款项支付。各部门主管对本部门报销真实性承担审核责任。")
    
    add_heading_styled(doc, "二、报销流程", 1)
    
    add_heading_styled(doc, "2.1 标准报销流程", 2)
    add_body(doc, "费用发生后 30 日内须完成报销申请，逾期原则上不予报销（特殊情况须经部门总监和财务总监会签审批）。标准报销流程为：① 报销人通过 OA 系统提交报销申请，填写费用明细、报销金额、费用归属项目或部门、报销事由，并上传合规发票图片（须清晰完整）；② 直属上级在 2 个工作日内审核费用真实性和合理性；③ 部门总监在 2 个工作日内复核审批（单笔金额超过 5000 元须加签财务总监审批）；④ 财务部会计审核发票合规性和金额准确性，审核不通过的退回并注明原因；⑤ 财务出纳在审核通过后 3 个工作日内完成打款。报销款统一转入员工工资卡，不支持现金支付。")
    
    add_heading_styled(doc, "2.2 加急报销", 2)
    add_body(doc, "因特殊原因确需加急处理的报销，报销人可在 OA 提交时勾选"加急"选项并注明加急原因。加急报销由财务部优先处理，审核通过后 1 个工作日内完成打款。每人每月加急报销次数原则上不超过 2 次。滥用加急渠道者，将被取消加急权限。")
    
    add_heading_styled(doc, "三、发票要求", 1)
    
    add_heading_styled(doc, "3.1 发票类型", 2)
    add_body(doc, "可报销票据类型：增值税专用发票、增值税普通发票、电子发票、定额发票、交通票据（机票行程单、火车票、汽车票等）及其他合法有效的原始凭证。增值税专用发票须同时取得发票联和抵扣联。电子发票须在税务局官方平台查验真伪并打印后作为附件上传。发票开具日期须在费用实际发生日期之后 15 日内。发票内容应与报销事项一致，不得以无关发票替代报销。")
    
    add_heading_styled(doc, "3.2 发票抬头", 2)
    add_body(doc, "发票抬头必须为公司全称"XX科技有限公司"。纳税人识别号：91110108XXXXXXXXXX。发票信息错误或不完整的一律退回重开。电子发票需在 OA 系统附件中同时上传 PDF 原件和打印件扫描件。发票金额须与报销金额一致（多张发票合计金额等于报销金额的情况除外）。")
    
    add_heading_styled(doc, "3.3 发票丢失处理", 2)
    add_body(doc, "增值税专用发票丢失：需联系开票方提供发票复印件并加盖开票方发票专用章，同时附上情况说明，由部门总监和财务总监审批后可替代报销。增值税普通发票丢失：需联系开票方重新开具电子发票或提供发票复印件加盖公章。交通票据（机票行程单、火车票等）丢失：国内机票可通过航空公司官网或第三方购票平台补打电子行程单；火车票可凭购票记录和情况说明报销，但报销金额的 20% 作为管理费扣除（单次最多扣 200 元）。发票丢失须在 5 个工作日内报告直属上级和财务部，故意隐瞒或拖延不报者按违规处理。")
    
    add_heading_styled(doc, "四、费用标准", 1)
    
    add_heading_styled(doc, "4.1 差旅费", 2)
    add_body(doc, "交通标准：城市间交通——员工级别 P5 及以下乘坐高铁二等座/飞机经济舱，P6-P8 乘坐高铁一等座/飞机经济舱，P9 及以上乘坐高铁商务座/飞机商务舱。住宿标准——一线城市（北上广深）：P5 及以下 400 元/晚，P6-P8 600 元/晚，P9 及以上 1000 元/晚；其他城市分别对应 300 元/晚、450 元/晚、800 元/晚。超出标准部分个人自理。住宿费须提供酒店住宿清单（水单）作为附件。出差期间餐饮补贴——按自然天数计算，每人每天 100 元（无需发票，随报销自动发放）；当日往返（不涉住宿）减半为 50 元/天。出差申请须提前在 OA 系统提交出差申请单，经部门总监审批后方可出差。")
    
    add_heading_styled(doc, "4.2 招待费", 2)
    add_body(doc, "商务招待须提前申请，填写招待申请单，注明招待对象（单位名称、姓名和职位）、招待目的、预计人数和预算金额。招待标准——普通客户：人均不超过 200 元；重要客户/合作伙伴：人均不超过 400 元；战略客户/政府机关：不受上述限制但须总经理审批。单次招待费用超过 3000 元的须提前报部门总监审批，超过 10000 元的须提前报总经理审批。招待费发票背面须注明招待对象和时间，两人以上共同招待的须在备注中写明参与人员。")
    
    add_heading_styled(doc, "4.3 办公用品", 2)
    add_body(doc, "各部门每季度可根据实际需求提交办公用品采购申请，由行政部统一采购。单次采购金额不超过 500 元的，可由个人先行垫付后凭票报销。超过 500 元的须走对公采购流程，由行政部统一采购入库后领用。办公用品包括但不限于：文具耗材（笔、本、文件夹等）、电脑外设（键盘、鼠标、耳机等，200 元以内）、打印纸墨等消耗品。非消耗性办公用品（如显示器、打印机等）属于固定资产，须走固定资产采购流程，不得以办公用品名义报销。")
    
    add_heading_styled(doc, "五、审批权限", 1)
    add_body(doc, "费用审批权限按金额和类型分级管理：单笔报销金额 2000 元以下——直属上级审批即可；2000-5000 元——直属上级+部门总监两级审批；5000-20000 元——在上述基础上加签财务总监；20000 元以上——在上述基础上最终由总经理审批。差旅费、招待费无论金额大小均须至少两级审批（直属上级+部门总监）。员工本人不得审批自己的报销申请；部门总监的报销须由其上级审批。审批人请假或出差期间，审批权限自动转交至其指定代理人或上一级管理者。")
    
    add_heading_styled(doc, "六、违规处理", 1)
    add_body(doc, "虚假报销（包括但不限于虚构费用、篡改发票金额、使用假发票、重复报销、将个人消费伪造成公务消费等），一经查实，取消当次报销资格，按虚报金额的 2 倍罚款（最低罚款 500 元），全公司通报批评，情节严重者解除劳动合同。审批人未尽审核义务导致违规报销通过的，审批人承担连带责任并扣除当月绩效分 5 分。财务部每季度随机抽查不少于当月报销总笔数 5% 的单据进行审计复核，审计结果在全公司通报。员工可通过公司举报邮箱（jiancha@公司域名.com）匿名举报违规报销行为，查证属实的给予举报人 500-5000 元奖励。")
    
    output_path = os.path.join(os.path.dirname(__file__), "财务报销制度.docx")
    doc.save(output_path)
    print(f"已生成：{output_path}")

if __name__ == "__main__":
    generate()
```

- [ ] **Step 2: 运行脚本**

```bash
cd "C:\Users\29542\Desktop\企业问答知识库\phase-b-dify\documents" && python 生成财务报销制度.py
```

- [ ] **Step 3: 验证文件存在**

---

### Task 6: 生成《新员工入职指南》TXT + Prompt 模板 + 测试问题 + 配置文件

**Files:**
- Create: `phase-b-dify/documents/新员工入职指南.txt`
- Create: `phase-b-dify/prompts/system-prompt.md`
- Create: `phase-b-dify/prompts/user-prompt.md`
- Create: `phase-b-dify/test-questions.md`
- Create: `phase-b-dify/dify-workflow-config.md`
- Create: `phase-b-dify/test-results.md`
- Create: `notes/rag-notes.md`

- [ ] **Step 1: 写入《新员工入职指南》TXT**

直接 Write 到 `phase-b-dify/documents/新员工入职指南.txt`，内容：

```
XX科技有限公司 - 新员工入职指南

欢迎加入XX科技！本指南将帮助你顺利完成入职流程。

一、入职前准备

1. 入职当天请携带以下材料：
   - 本人身份证原件及复印件（正反面，2份）
   - 最高学历学位证书原件及复印件（1份）
   - 近期一寸免冠白底照片（2张，电子版也请备好）
   - 本人名下的银行卡（用于发工资，必须是本人账户）
   - 上一家单位的离职证明（如有）

2. 入职时间：周一至周五上午 9:00，请准时到达公司前台。
   公司地址：XX市XX区XX路XX号XX大厦 15-18 层
   前台电话：010-XXXX-XXXX

3. 着装建议：商务休闲即可，第一天建议稍微正式一些。

二、入职当天流程

1. 9:00 - 9:30  前台签到，HR 接待，填写入职登记表
2. 9:30 - 10:00 签订劳动合同、保密协议和竞业限制协议（如有）
3. 10:00 - 10:30 HR 讲解公司组织架构、企业文化、薪酬福利政策
4. 10:30 - 11:00 IT 部门分配电脑和办公设备，创建系统账号
5. 11:00 - 11:30 行政部带领参观办公环境，介绍各功能区
6. 11:30 - 13:00 与部门同事午餐（公司食堂 B1 层，餐补自动打入工卡）
7. 13:00 - 14:00 部门主管介绍部门职责和团队分工
8. 14:00 - 17:00 参加新员工入职培训（安全培训+IT系统培训）

三、系统账号说明

入职当天 IT 部门将为你创建以下系统账号，账号名为"姓名全拼@公司域名"：

| 系统 | 用途 | 初始密码 |
|------|------|----------|
| 企业邮箱 | 工作邮件收发 | 身份证后6位+Ab |
| OA 系统 | 请假、报销、审批等 | 身份证后6位+Ab |
| 云办公平台 | 沟通协作 | 身份证后6位+Ab |
| 代码仓库 | 开发人员专用 | 单独分配 |
| 文件服务器 | 文件存储与共享 | 同 OA |

首次登录各系统后请立即修改密码，密码要求：不少于12位，含大小写字母+数字+特殊符号中至少3类。

四、电脑与设备

入职当天 IT 部门将提供以下设备（请在设备交接单上签字确认）：
- 笔记本电脑一台（ThinkPad X1 Carbon / MacBook Pro，根据岗位配置）
- 外接显示器一台（27寸 4K）
- 键盘鼠标套装
- 耳机一副
- 工牌一张（用于门禁和食堂消费）

IT 部门已预装必要的办公软件（Office 套件、企业微信、CloudWork、杀毒软件等）。如需安装额外软件，请通过 OA 系统提交软件安装申请，IT 部门将在 1 个工作日内处理。未经 IT 部门许可，不得自行安装盗版或未经授权的软件。公司电脑默认安装了设备管理软件和加密软件，请勿尝试卸载或禁用。

五、第一周建议

1. 熟悉公司产品和服务：阅读产品手册和公司官网，了解公司核心业务
2. 了解团队工作流程：向直属上级了解团队的目标、当前项目和技术栈
3. 建立人际关系：主动约同事午餐或喝咖啡，至少认识 10 位同事
4. 阅读部门文档：熟悉部门的文档规范和代码规范（如适用）
5. 设置个人工作环境：配置开发工具、浏览器书签、邮箱签名等
6. 周五前与直属上级进行一次 one-on-one，沟通入职感受和下一步工作安排

六、常见问题

Q：食堂在哪里？什么时间开放？
A：食堂位于公司大楼 B1 层，午餐 11:30-13:00，晚餐 17:30-19:00。餐补 20 元/工作日自动打入工卡。支持工卡和微信/支付宝支付。

Q：健身房怎么使用？
A：公司健身房位于 12 层，开放时间 6:30-22:00。刷工卡进入，配有淋浴间。每周三、周五有瑜伽/健身操课程，请关注企业微信群通知。

Q：电脑坏了找谁？
A：联系 IT 服务台：企业微信搜索"IT服务台"或拨打分机 8888。IT 部门提供 7x24 小时紧急技术支持。一般故障 2 小时内响应，硬件故障提供备用机。

Q：试用期多久？考核标准是什么？
A：一般岗位试用期为 3 个月，高级岗位为 6 个月。试用期考核包括：工作能力（50%）、学习态度（25%）、团队融合（25%）。第 1 个月末进行一次中期评估，第 3 个月末进行转正答辩。具体考核标准请参见《试用期考核管理办法》。

Q：我不小心删了重要文件怎么办？
A：立即联系 IT 部门（分机 8888），不要对电脑做任何其他操作。文件服务器上的文件有每日备份，可申请恢复。本地文件如果启用了 OneDrive/CloudWork 同步，可在回收站中找回。

如有任何疑问，请随时联系 HR 或你的直属上级。祝你入职顺利，工作愉快！
```

- [ ] **Step 2: 写入 System Prompt 模板**

Write 到 `phase-b-dify/prompts/system-prompt.md`，内容即设计文档中的系统提示词。

- [ ] **Step 3: 写入 User Prompt 模板**

Write 到 `phase-b-dify/prompts/user-prompt.md`，内容即设计文档中的用户提示词。

- [ ] **Step 4: 写入测试问题集**

Write 到 `phase-b-dify/test-questions.md`，10 题 + 预期答案来源。

- [ ] **Step 5: 写入工作流配置记录模板**

Write 到 `phase-b-dify/dify-workflow-config.md`，包含节点参数表（空值待填写）。

- [ ] **Step 6: 写入测试结果记录模板**

Write 到 `phase-b-dify/test-results.md`，包含 10 行结果表格。

- [ ] **Step 7: 写入学习笔记模板**

Write 到 `notes/rag-notes.md`，包含 RAG 概念框架、关键参数表等。

---

### Task 7: Dify 知识库创建与文档上传（用户手动操作）

> 此任务由用户在 Dify Web UI 中操作，我来截图指导。

**操作步骤预览：**
1. 登录 http://localhost → 进入 Dify
2. 顶部导航 → "知识库" → "创建知识库"
3. 上传 5 份文档
4. 配置分片参数（chunk_size=500, overlap=100）
5. 等待嵌入处理完成
6. 创建"聊天助手"类型应用，关联知识库
7. 配置 Prompt 模板（复制粘贴）
8. 测试问答

---

### Task 8: 测试验证与结果记录

- [ ] 逐题测试 10 个问题
- [ ] 记录每个答案
- [ ] 判定是否准确（有据可查 = 准确，瞎编/找不到 = 不准确）
- [ ] 计算准确率 = 准确题数 / 总题数
- [ ] 目标准确率 85%+（即 10 题中至少 9 题准确）
