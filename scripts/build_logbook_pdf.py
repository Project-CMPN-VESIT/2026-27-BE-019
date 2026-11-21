import os
import subprocess
import base64

def generate_logbook():
    logo_path = os.path.abspath('extracted_logbook_assets/image1.png')
    logo_b64 = ""
    if os.path.exists(logo_path):
        with open(logo_path, 'rb') as f:
            logo_b64 = base64.b64encode(f.read()).decode('utf-8')

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>CAPSTONE PROJECT LOGBOOK - Group 19</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 20mm 15mm 20mm 15mm;
    @bottom-center {{
      content: counter(page);
    }}
  }}
  body {{
    font-family: 'Times New Roman', Times, serif;
    font-size: 11pt;
    line-height: 1.35;
    color: #111;
    margin: 0;
    padding: 0;
  }}
  .page {{
    page-break-after: always;
    min-height: 90vh;
  }}
  .page:last-child {{
    page-break-after: avoid;
  }}
  .center {{
    text-align: center;
  }}
  .bold {{
    font-weight: bold;
  }}
  h1, h2, h3, h4 {{
    margin: 6px 0;
    text-align: center;
    font-weight: bold;
  }}
  h1 {{ font-size: 15pt; text-transform: uppercase; }}
  h2 {{ font-size: 13pt; }}
  h3 {{ font-size: 12pt; }}
  h4 {{ font-size: 11.5pt; }}
  p {{
    margin: 5px 0;
    text-align: justify;
  }}
  .logo {{
    display: block;
    margin: 12px auto;
    width: 110px;
    height: auto;
  }}
  table {{
    width: 100%;
    border-collapse: collapse;
    margin: 8px 0;
    font-size: 9.5pt;
  }}
  table, th, td {{
    border: 1px solid #222;
  }}
  th, td {{
    padding: 4px 6px;
    vertical-align: top;
  }}
  th {{
    background-color: #f2f2f2;
    text-align: center;
    font-weight: bold;
  }}
  .sign-container {{
    display: flex;
    justify-content: space-between;
    margin-top: 35px;
  }}
  .sign-box {{
    text-align: center;
    width: 30%;
  }}
  .student-sign-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 30px 20px;
    margin-top: 25px;
  }}
  .student-sign-box {{
    text-align: center;
  }}
  .divider {{
    border-top: 1px solid #333;
    margin: 10px 0;
  }}
</style>
</head>
<body>

<!-- PAGE 1: COVER PAGE -->
<div class="page center">
  <div style="font-size: 13pt; font-weight: bold; line-height: 1.4;">
    VIVEKANAND EDUCATION SOCIETY'S INSTITUTE OF TECHNOLOGY<br>
    <span style="font-size: 11pt; font-weight: normal;">(An Autonomous Institute Affiliated to the University of Mumbai)</span><br>
    DEPARTMENT OF COMPUTER ENGINEERING
  </div>
  
  <br>
  <img src="data:image/png;base64,{logo_b64}" class="logo" alt="VESIT Logo">
  <br>

  <h1 style="font-size: 18pt; letter-spacing: 1px;">CAPSTONE PROJECT LOGBOOK</h1>
  <div style="font-size: 13pt; font-weight: bold; color: #333;">(26CMCP71 : Capstone Project - II)</div>
  <div style="font-size: 14pt; font-weight: bold; margin-top: 5px;">Academic Year 2026–27</div>

  <br><br>
  <div style="text-align: left; margin: 0 auto; width: 85%; border: 1.5px solid #222; padding: 18px 24px; background: #fafafa;">
    <div style="font-size: 12pt; font-weight: bold; text-decoration: underline; margin-bottom: 8px;">GROUP MEMBERS (Group No. 19):</div>
    <div style="font-size: 11.5pt; line-height: 1.7;">
      1. <b>Jass Shivnani</b> (D17B - 50)<br>
      2. <b>Riya Khialani</b> (D17A - 34)<br>
      3. <b>Ruchika Dingria</b> (D17B - 70)<br>
      4. <b>Khushi Sadhuramani</b> (D17B - 44)
    </div>
    
    <div style="margin-top: 16px; font-size: 12pt;">
      <b>Project Title:</b> Large Action Model (LAM) Engine: Dione
    </div>
    <div style="margin-top: 10px; font-size: 12pt;">
      <b>Project Mentor:</b> Dr. Geocey Shejy (Associate Professor)
    </div>
  </div>
</div>

<!-- PAGE 2: VISION, MISSION, PEOs, POs, PSOs -->
<div class="page">
  <h3>INSTITUTE VISION & MISSION</h3>
  <p><b>VISION:</b> To build a vibrant, knowledge-driven ecosystem that promotes holistic learning, inspires innovation, practices sustainability and value-based education, and shapes socially conscious, industry-ready technocrats.</p>
  <p><b>MISSION:</b><br>
  • To inculcate a culture of multidisciplinary value based education.<br>
  • To inspire students to apply their knowledge to meet the needs of industry and society.<br>
  • To foster research, entrepreneurship and lifelong learning for societal growth.</p>

  <h3>COMPUTER ENGINEERING DEPARTMENT</h3>
  <p><b>VISION:</b> To establish a center of excellence in computing by empowering students with advanced technological skills for fostering innovation, research, and societal impact.</p>
  <p><b>MISSION:</b><br>
  • To cultivate a teaching learning environment that unites theory with computing skills, empowering students to adapt to evolving technologies.<br>
  • To strengthen core computing knowledge by fostering research, innovation, and entrepreneurship through multi-disciplinary learning.<br>
  • To prepare competent professionals with industry-ready skills, encouraging social awareness, sustainable development, and a commitment to lifelong learning.</p>

  <h3>PROGRAM EDUCATIONAL OBJECTIVES (PEOs)</h3>
  <table>
    <tr><th style="width: 10%;">PEO</th><th>Description</th></tr>
    <tr><td class="center"><b>I</b></td><td>To equip Computer Engineering students with a strong foundation in mathematics, science, and core computing and engineering principles, enabling them to comprehend, analyze, and design effective technology-driven solutions.</td></tr>
    <tr><td class="center"><b>II</b></td><td>To foster a multidisciplinary mindset in Computer Engineering students through flexible learning, enabling adaptability along with strong communication, teamwork, and leadership skills.</td></tr>
    <tr><td class="center"><b>III</b></td><td>To empower Computer Engineering students with advanced computing and software skills, fostering innovation, entrepreneurship, and sustainable practices for lifelong learning.</td></tr>
    <tr><td class="center"><b>IV</b></td><td>To provide Computer Engineering students with broad educational and research experiences through academic and industrial collaboration programs, preparing them for industry-ready careers.</td></tr>
  </table>

  <h3>PROGRAM SPECIFIC OUTCOMES (PSOs)</h3>
  <table>
    <tr><th style="width: 15%;">PSO Code</th><th>Description</th></tr>
    <tr><td class="center"><b>PSO1</b></td><td><b>Professional Skills</b> - The ability to develop programs for computer based systems of varying complexity and domains using standard practices.</td></tr>
    <tr><td class="center"><b>PSO2</b></td><td><b>Successful Career</b> - The ability to adopt skills, languages, environment and platforms for creating innovative career paths, being successful entrepreneurs or for pursuing higher studies.</td></tr>
  </table>
</div>

<!-- PAGE 3: PROGRAM OUTCOMES (POs) -->
<div class="page">
  <h3>PROGRAM OUTCOMES (POs)</h3>
  <table>
    <tr><th style="width: 12%;">PO Code</th><th>Program Outcome Description</th></tr>
    <tr><td class="center"><b>PO1</b></td><td><b>Engineering Knowledge:</b> Apply knowledge of mathematics, natural science, computing, engineering fundamentals and an engineering specialization as specified in WK1 to WK4 respectively to develop the solution of complex engineering problems.</td></tr>
    <tr><td class="center"><b>PO2</b></td><td><b>Problem Analysis:</b> Identify, formulate, review research literature and analyze complex engineering problems reaching substantiated conclusions with consideration for sustainable development. (WK1 to WK4)</td></tr>
    <tr><td class="center"><b>PO3</b></td><td><b>Design/Development of Solutions:</b> Design creative solutions for complex engineering problems and design/develop systems/components/processes to meet identified needs with consideration for the public health and safety, whole-life cost, net zero carbon, culture, society and environment as required. (WK5)</td></tr>
    <tr><td class="center"><b>PO4</b></td><td><b>Conduct Investigations of Complex Problems:</b> Conduct investigations of complex engineering problems using research-based knowledge including design of experiments, modelling, analysis & interpretation of data to provide valid conclusions. (WK8)</td></tr>
    <tr><td class="center"><b>PO5</b></td><td><b>Engineering Tool Usage:</b> Create, select and apply appropriate techniques, resources and modern engineering & IT tools, including prediction and modelling recognizing their limitations to solve complex engineering problems. (WK2 and WK6)</td></tr>
    <tr><td class="center"><b>PO6</b></td><td><b>The Engineer and The World:</b> Analyze and evaluate societal and environmental aspects while solving complex engineering problems for its impact on sustainability with reference to economy, health, safety, legal framework, culture and environment. (WK1, WK5, and WK7)</td></tr>
    <tr><td class="center"><b>PO7</b></td><td><b>Ethics:</b> Apply ethical principles and commit to professional ethics, human values, diversity and inclusion; adhere to national & international laws. (WK9)</td></tr>
    <tr><td class="center"><b>PO8</b></td><td><b>Individual and Collaborative Team work:</b> Function effectively as an individual, and as a member or leader in diverse/multi-disciplinary teams.</td></tr>
    <tr><td class="center"><b>PO9</b></td><td><b>Communication:</b> Communicate effectively and inclusively within the engineering community and society at large, such as being able to comprehend and write effective reports and design documentation, make effective presentations considering cultural, language, and learning differences.</td></tr>
    <tr><td class="center"><b>PO10</b></td><td><b>Project Management and Finance:</b> Apply knowledge and understanding of engineering management principles and economic decision-making and apply these to one’s own work, as a member and leader in a team, and to manage projects in multidisciplinary environments.</td></tr>
    <tr><td class="center"><b>PO11</b></td><td><b>Life-Long Learning:</b> Recognize the need for, and have the preparation and ability for i) independent and life-long learning ii) adaptability to new and emerging technologies and iii) critical thinking in the broadest context of technological change. (WK8)</td></tr>
  </table>
</div>

<!-- PAGE 4: STUDENT INFO, INSTRUCTIONS, DECLARATION -->
<div class="page">
  <h3>STUDENT INFORMATION</h3>
  <p><b>Project Title:</b> Large Action Model (LAM) Engine: Dione &nbsp;&nbsp;|&nbsp;&nbsp; <b>SDGs Mapped:</b> SDG 8 – Decent Work & Economic Growth</p>
  <table>
    <tr>
      <th>Details</th>
      <th>Student 1</th>
      <th>Student 2</th>
      <th>Student 3</th>
      <th>Student 4</th>
    </tr>
    <tr>
      <td><b>Roll No.</b></td>
      <td class="center">34</td>
      <td class="center">50</td>
      <td class="center">70</td>
      <td class="center">44</td>
    </tr>
    <tr>
      <td><b>Name</b></td>
      <td>Riya Khialani</td>
      <td>Jass Shivnani</td>
      <td>Ruchika Dingria</td>
      <td>Khushi Sadhuramani</td>
    </tr>
    <tr>
      <td><b>Class & Div</b></td>
      <td class="center">D17A</td>
      <td class="center">D17B</td>
      <td class="center">D17B</td>
      <td class="center">D17B</td>
    </tr>
    <tr>
      <td><b>Contact No.</b></td>
      <td>9699749462</td>
      <td>7709770107</td>
      <td>7709618412</td>
      <td>7709190679</td>
    </tr>
    <tr>
      <td><b>E-mail</b></td>
      <td>2023.riya.khialani@ves.ac.in</td>
      <td>2023.jass.shivnani@ves.ac.in</td>
      <td>d2023.ruchika.dingria@ves.ac.in</td>
      <td>2023.khushi.sadhuramani@ves.ac.in</td>
    </tr>
    <tr>
      <td><b>Address</b></td>
      <td>202, Dhan Guru Nanak Shah Palace, Gandhi Road, Ulhasnagar 5</td>
      <td>402, Sai Empire, Near Heena Medical, Hum Log Circle, Ulhasnagar 4</td>
      <td>Bk no.941, Room no.16, Sec 22, Near Kanwaram Chowk, Ulhasnagar 3</td>
      <td>103, Devika Towers, Collectors Colony, Chembur, Mumbai</td>
    </tr>
  </table>

  <h3>INSTRUCTIONS TO STUDENTS:</h3>
  <p>1. The logbook must be submitted to the Project Mentor or Project Coordinator for verification and evaluation of project activities at least once in a week.<br>
  2. A logbook duly signed by the project mentor must be submitted with a project blackbook for evaluation at the end of semester to the department.</p>

  <h3>DECLARATION</h3>
  <p>I declare that this project represents my ideas in my own words and wherever others' ideas or words have been included, I have adequately cited and referenced the original sources. I also declare that I have adhered to all principles of academic honesty and integrity and have not misrepresented or fabricated or falsified any idea/data/fact/source in my project work. I promise to maintain minimum 75% attendance, as per the Institute norms. I understand that any violation of the above will be cause for disciplinary action by the Institute.</p>
  
  <p><b>Yours Faithfully,</b></p>
  <div class="student-sign-grid">
    <div class="student-sign-box">
      <br>____________________________<br>
      <b>Jass Shivnani</b> (D17B - 50)
    </div>
    <div class="student-sign-box">
      <br>____________________________<br>
      <b>Riya Khialani</b> (D17A - 34)
    </div>
    <div class="student-sign-box">
      <br>____________________________<br>
      <b>Ruchika Dingria</b> (D17B - 70)
    </div>
    <div class="student-sign-box">
      <br>____________________________<br>
      <b>Khushi Sadhuramani</b> (D17B - 44)
    </div>
  </div>
</div>

<!-- PAGE 5: LETTER OF ACCEPTANCE -->
<div class="page">
  <h3>LETTER OF ACCEPTANCE</h3>
  <br>
  <p>I undersigned, <b>Dr. Geocey Shejy</b> working in the Computer Engineering department, willing to guide the Project titled <b>Large Action Model (LAM) Engine: Dione</b> for the Capstone Project - II Semester VII respectively for the Academic Year 2026-27. The names of the students are:</p>
  <br>
  <div style="margin-left: 40px; font-size: 11pt; line-height: 1.8;">
    1. <b>Jass Shivnani</b> (D17B - 50)<br>
    2. <b>Riya Khialani</b> (D17A - 34)<br>
    3. <b>Khushi Sadhuramani</b> (D17B - 44)<br>
    4. <b>Ruchika Dingria</b> (D17B - 70)
  </div>

  <br><br><br><br>
  <div class="sign-container">
    <div class="sign-box">
      ____________________________<br>
      <b>(Dr. Geocey Shejy)</b><br>
      Project Mentor
    </div>
    <div class="sign-box">
      ____________________________<br>
      <b>Capstone Project Coordinator</b><br>
      Department of Computer Engineering
    </div>
    <div class="sign-box">
      ____________________________<br>
      <b>(Dr. Nupur Giri)</b><br>
      HOD, Computer Engineering
    </div>
  </div>
</div>

<!-- PAGE 6: COURSE OUTCOMES & CO-PO MAPPING -->
<div class="page">
  <h3>COURSE OUTCOMES FOR CAPSTONE PROJECT–II</h3>
  <table>
    <tr><th style="width: 10%;">CO Code</th><th>Description</th><th style="width: 25%;">POs Covered</th><th style="width: 15%;">PSOs Covered</th></tr>
    <tr><td class="center"><b>CO1</b></td><td>Implement and integrate all modules of the proposed system effectively.</td><td>PO1, PO2, PO3, PO5</td><td>PSO1, PSO2</td></tr>
    <tr><td class="center"><b>CO2</b></td><td>Perform testing, debugging, validation, and performance optimization of the developed solution.</td><td>PO2, PO3, PO4, PO5</td><td>PSO1, PSO2</td></tr>
    <tr><td class="center"><b>CO3</b></td><td>Analyze project outcomes using appropriate engineering tools and metrics.</td><td>PO2, PO4, PO5</td><td>PSO1, PSO2</td></tr>
    <tr><td class="center"><b>CO4</b></td><td>Demonstrate deployment readiness, usability, security, scalability, and sustainability considerations.</td><td>PO3, PO5, PO6, PO7</td><td>PSO1, PSO2</td></tr>
    <tr><td class="center"><b>CO5</b></td><td>Analyze, interpret, and present research outcomes effectively using appropriate research methodologies, analytical tools, and presentation techniques.</td><td>PO2, PO4, PO5, PO8, PO10</td><td>PSO1, PSO2</td></tr>
    <tr><td class="center"><b>CO6</b></td><td>Present and defend the complete project professionally through demonstrations, presentations, and comprehensive technical documentation.</td><td>PO8, PO9, PO10, PO11</td><td>PSO1, PSO2</td></tr>
  </table>

  <h3>CO–PO–PSO MAPPING TABLE</h3>
  <table>
    <tr>
      <th>CO</th><th>PO1</th><th>PO2</th><th>PO3</th><th>PO4</th><th>PO5</th><th>PO6</th><th>PO7</th><th>PO8</th><th>PO9</th><th>PO10</th><th>PO11</th><th>PSO1</th><th>PSO2</th>
    </tr>
    <tr><td class="center"><b>CO1</b></td><td class="center">2</td><td class="center">3</td><td class="center">3</td><td class="center">–</td><td class="center">3</td><td class="center">–</td><td class="center">–</td><td class="center">–</td><td class="center">3</td><td class="center">–</td><td class="center">2</td><td class="center">3</td><td class="center">3</td></tr>
    <tr><td class="center"><b>CO2</b></td><td class="center">2</td><td class="center">3</td><td class="center">2</td><td class="center">3</td><td class="center">3</td><td class="center">–</td><td class="center">–</td><td class="center">–</td><td class="center">2</td><td class="center">–</td><td class="center">2</td><td class="center">3</td><td class="center">2</td></tr>
    <tr><td class="center"><b>CO3</b></td><td class="center">2</td><td class="center">3</td><td class="center">2</td><td class="center">3</td><td class="center">3</td><td class="center">–</td><td class="center">–</td><td class="center">–</td><td class="center">–</td><td class="center">2</td><td class="center">2</td><td class="center">3</td><td class="center">2</td></tr>
    <tr><td class="center"><b>CO4</b></td><td class="center">2</td><td class="center">2</td><td class="center">3</td><td class="center">2</td><td class="center">3</td><td class="center">2</td><td class="center">3</td><td class="center">2</td><td class="center">–</td><td class="center">–</td><td class="center">3</td><td class="center">3</td><td class="center">3</td></tr>
    <tr><td class="center"><b>CO5</b></td><td class="center">2</td><td class="center">3</td><td class="center">–</td><td class="center">3</td><td class="center">3</td><td class="center">–</td><td class="center">–</td><td class="center">2</td><td class="center">–</td><td class="center">3</td><td class="center">2</td><td class="center">2</td><td class="center">2</td></tr>
    <tr><td class="center"><b>CO6</b></td><td class="center">–</td><td class="center">–</td><td class="center">–</td><td class="center">–</td><td class="center">2</td><td class="center">–</td><td class="center">–</td><td class="center">2</td><td class="center">3</td><td class="center">3</td><td class="center">2</td><td class="center">2</td><td class="center">2</td></tr>
  </table>
  <p style="font-size: 8.5pt;"><i>Mapping scale: 3 = High correlation; 2 = Moderate correlation; 1 = Low correlation; – = No direct correlation.</i></p>
</div>

<!-- PAGE 7: SCHEDULE FOR CAPSTONE PROJECT - II -->
<div class="page">
  <h3>SCHEDULE FOR CAPSTONE PROJECT - II</h3>
  <table>
    <tr>
      <th style="width: 14%;">Date</th>
      <th style="width: 8%;">Week</th>
      <th>Contents</th>
      <th style="width: 25%;">Remark</th>
      <th style="width: 14%;">Guide Sign</th>
    </tr>
    <tr><td class="center">11/08/2026</td><td class="center">1</td><td>Reviewed existing Dione system and planned enhancements.</td><td>Planning completed</td><td></td></tr>
    <tr><td class="center">18/08/2026</td><td class="center">2</td><td>Finalization of development milestones and features.</td><td>Requirements finalized</td><td></td></tr>
    <tr><td class="center">25/08/2026</td><td class="center">3</td><td>LAM architecture and LLM integration.</td><td>Architecture improved</td><td></td></tr>
    <tr><td class="center">01/09/2026</td><td class="center">4</td><td>ReAct-based orchestration and task execution.</td><td>Workflow enhanced</td><td></td></tr>
    <tr><td class="center">08/09/2026</td><td class="center">5</td><td>Voice interaction and audio responses.</td><td>Voice module added</td><td></td></tr>
    <tr><td class="center">15/09/2026</td><td class="center">6</td><td>Device access and computer automation.</td><td>Automation developed</td><td></td></tr>
    <tr><td class="center">22/09/2026</td><td class="center">7</td><td>YouTube playback and MS Paint automation.</td><td>Applications integrated</td><td></td></tr>
    <tr><td class="center">29/09/2026</td><td class="center">8</td><td>Multi-plugin integration and orchestration.</td><td>Plugins integrated</td><td></td></tr>
    <tr><td class="center">06/10/2026</td><td class="center">9</td><td>Safety Kernel, guardrails and permissions.</td><td>Safety improved</td><td></td></tr>
    <tr><td class="center">13/10/2026</td><td class="center">10</td><td>Memory and contextual task handling.</td><td>Memory enhanced</td><td></td></tr>
    <tr><td class="center">20/10/2026</td><td class="center">11</td><td>System integration, testing and debugging.</td><td>Testing completed</td><td></td></tr>
    <tr><td class="center">27/10/2026</td><td class="center">12</td><td>Final implementation and project demonstration.</td><td>Project ready for final review</td><td></td></tr>
  </table>
</div>

<!-- PAGE 8: PROGRESS / ATTENDANCE REPORT -->
<div class="page">
  <h3>PROGRESS / ATTENDANCE REPORT</h3>
  <table>
    <tr>
      <td colspan="2"><b>Title of the Project:</b> Large Action Model (LAM) Engine: Dione</td>
    </tr>
    <tr>
      <td style="width: 25%;"><b>Group No.:</b> 19</td>
      <td>1. Jass Shivnani (D17B - 50) &nbsp;&nbsp; 2. Riya Khialani (D17A - 34)<br>3. Ruchika Dingria (D17B - 70) &nbsp;&nbsp; 4. Khushi Sadhuramani (D17B - 44)</td>
    </tr>
    <tr>
      <td colspan="2"><b>Name of the Project Mentor:</b> Dr. Geocey Shejy</td>
    </tr>
  </table>

  <table>
    <tr>
      <th rowspan="2" style="width: 6%;">Sr. No</th>
      <th rowspan="2" style="width: 11%;">Date</th>
      <th colspan="4" style="width: 16%;">Attendance</th>
      <th rowspan="2">Progress / Suggestion</th>
      <th colspan="3" style="width: 20%;">Mapping</th>
    </tr>
    <tr>
      <th>1</th><th>2</th><th>3</th><th>4</th>
      <th>CO</th><th>PO</th><th>PSO</th>
    </tr>
    <tr><td class="center">1</td><td class="center">11/08/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Review existing Dione implementation and plan improvements.</td><td class="center">CO1</td><td>PO1, PO2, PO3, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">2</td><td class="center">18/08/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Finalize additional features and development milestones.</td><td class="center">CO1</td><td>PO1, PO2, PO3, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">3</td><td class="center">25/08/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Improve LAM architecture and LLM integration.</td><td class="center">CO1</td><td>PO1, PO2, PO3, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">4</td><td class="center">01/09/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Enhance orchestration and multistep execution.</td><td class="center">CO1</td><td>PO1, PO2, PO3, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">5</td><td class="center">08/09/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Integrate voice commands and audio responses.</td><td class="center">CO1</td><td>PO1, PO2, PO3, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">6</td><td class="center">15/09/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Enable device access and application control.</td><td class="center">CO1, CO4</td><td>PO1, PO2, PO3, PO5, PO6, PO7</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">7</td><td class="center">22/09/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Implement YouTube and MS Paint automation.</td><td class="center">CO1, CO4</td><td>PO1, PO2, PO3, PO5, PO6, PO7</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">8</td><td class="center">29/09/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Improve plugin coordination and tool execution.</td><td class="center">CO1</td><td>PO1, PO2, PO3, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">9</td><td class="center">06/10/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Strengthen guardrails and permission checks.</td><td class="center">CO4</td><td>PO3, PO5, PO6, PO7</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">10</td><td class="center">13/10/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Improve memory and contextual understanding.</td><td class="center">CO3</td><td>PO2, PO4, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">11</td><td class="center">20/10/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Perform integration testing and debugging.</td><td class="center">CO2</td><td>PO2, PO3, PO4, PO5</td><td class="center">PSO1, PSO2</td></tr>
    <tr><td class="center">12</td><td class="center">27/10/2026</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td class="center">P</td><td>Complete improvements and prepare demonstration.</td><td class="center">CO6</td><td>PO8, PO9, PO10, PO11</td><td class="center">PSO1, PSO2</td></tr>
  </table>

  <br>
  <div style="text-align: right; margin-top: 20px;">
    ____________________________<br>
    <b>Sign of the Project Mentor</b>
  </div>
</div>

<!-- PAGE 9: EXAMINER'S FEEDBACK FORM -->
<div class="page">
  <h3>EXAMINER'S FEEDBACK FORM</h3>
  <table style="margin-bottom: 12px;">
    <tr>
      <td><b>Name of External Examiner:</b> ___________________________</td>
      <td><b>College of External Examiner:</b> ___________________________</td>
    </tr>
    <tr>
      <td><b>Name of Internal Examiner:</b> ___________________________</td>
      <td><b>Date of Examination:</b> 21 / 11 / 2026</td>
    </tr>
    <tr>
      <td><b>No. of Students in Project Team:</b> 4</td>
      <td><b>Availability of Separate Lab for Project:</b> Yes / No</td>
    </tr>
  </table>

  <p><b>Student Performance Analysis (Put Tick as per your Observation)</b></p>
  <table>
    <tr>
      <th style="width: 8%;">Sr. No.</th>
      <th>Observation</th>
      <th style="width: 14%;">Excellent (3)</th>
      <th style="width: 14%;">Very Good (2)</th>
      <th style="width: 14%;">Good (1)</th>
    </tr>
    <tr><td class="center">1</td><td>Quality of problem and Complex Engineering Problems</td><td></td><td></td><td></td></tr>
    <tr><td class="center">2</td><td>Innovativeness in solutions</td><td></td><td></td><td></td></tr>
    <tr><td class="center">3</td><td>Cost effectiveness and Societal impact</td><td></td><td></td><td></td></tr>
    <tr><td class="center">4</td><td>Full functioning of working model as per stated requirements</td><td></td><td></td><td></td></tr>
    <tr><td class="center">5</td><td>Effective use of skill sets</td><td></td><td></td><td></td></tr>
    <tr><td class="center">6</td><td>Effective use of standard engineering norms</td><td></td><td></td><td></td></tr>
    <tr><td class="center">7</td><td>Contribution of an individual as member or leader</td><td></td><td></td><td></td></tr>
    <tr><td class="center">8</td><td>Clarity in written and oral communication</td><td></td><td></td><td></td></tr>
    <tr><td class="center">9</td><td>Overall performance</td><td></td><td></td><td></td></tr>
  </table>

  <br>
  <p><b>Suggest new Innovative Technique / Idea / Objectives related to this project:</b></p>
  <div style="border: 1px solid #777; height: 75px; width: 100%; margin-top: 5px;"></div>

  <br><br><br>
  <div class="sign-container">
    <div class="sign-box" style="width: 45%;">
      ____________________________________<br>
      <b>Signature of External Examiner</b>
    </div>
    <div class="sign-box" style="width: 45%;">
      ____________________________________<br>
      <b>Signature of Internal Examiner</b>
    </div>
  </div>
</div>

</body>
</html>
"""

    html_file = os.path.abspath('logbook_render.html')
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print("Generated HTML:", html_file)

    # Output paths
    edge = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
    
    # 1. Output file named exactly as requested:
    # 19-AI, Deep Learning & DWH Mining- Dr. Geocey.pdf
    filename_pdf = "19-AI, Deep Learning & DWH Mining- Dr. Geocey.pdf"
    
    # Directories
    dirs = [
        os.path.abspath(r'docs\19-AI, Deep Learning & DWH Mining- Dr. Geocey - Log Book'),
        os.path.abspath(r'docs\Log Book'),
        os.path.abspath(r'C:\Users\Jass\Downloads\19-AI, Deep Learning & DWH Mining- Dr. Geocey - Log Book')
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)
        pdf_out = os.path.join(d, filename_pdf)
        cmd = [
            edge,
            '--headless',
            '--disable-gpu',
            f'--print-to-pdf={pdf_out}',
            f'file:///{html_file}'
        ]
        res = subprocess.run(cmd, capture_output=True, text=True)
        print(f"Generated Logbook PDF at {pdf_out}: exists={os.path.exists(pdf_out)}, size={os.path.getsize(pdf_out) if os.path.exists(pdf_out) else 0}")

if __name__ == '__main__':
    generate_logbook()
