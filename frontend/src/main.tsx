import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import {
  LayoutDashboard, Users, WalletCards, CalendarDays, FileSpreadsheet,
  Upload, Bot, Settings, ShieldCheck, Plus, RefreshCw, Calculator,
  Download, CheckCircle2, CircleAlert, X, ReceiptText
} from "lucide-react";
import "./styles.css";

const API = "/api/v1";
type Employee = { id:number; full_name:string; position:string; hire_date:string; salary:number; employment_rate:number; vacation_balance:number; active:boolean };
type Dash = { employees:number; payroll_ready:boolean; active_salary:number; vacation_days:number };

const menu = [
  ["Обзор", LayoutDashboard], ["Сотрудники", Users], ["Зарплата", WalletCards],
  ["Календарь и табель", CalendarDays], ["Кадры", ShieldCheck], ["Налоги", ReceiptText],
  ["1С / Обмен", Upload], ["Отчёты", FileSpreadsheet], ["Помощник", Bot]
] as const;

const money=(n:number)=>new Intl.NumberFormat("ru-RU",{style:"currency",currency:"RUB",maximumFractionDigits:0}).format(n||0);

function App(){
  const [active,setActive]=useState("Обзор");
  const [dash,setDash]=useState<Dash|null>(null);
  const [employees,setEmployees]=useState<Employee[]>([]);
  const [loading,setLoading]=useState(false);
  const [message,setMessage]=useState("");
  const load=async()=>{setLoading(true);try{
    const [d,e]=await Promise.all([fetch(API+"/dashboard"),fetch(API+"/employees")]);
    if(d.ok)setDash(await d.json()); if(e.ok)setEmployees(await e.json());
  }finally{setLoading(false)}};
  useEffect(()=>{load()},[]);
  const refresh=()=>{setMessage("");load()};
  return <div className="app">
    <aside>
      <div className="brand"><div className="logo">LL</div><div><b>Laser Love</b><span>Finance</span></div></div>
      <nav>{menu.map(([name,Icon])=><button key={name} className={active===name?"active":""} onClick={()=>setActive(name)}><Icon size={18}/><span>{name}</span></button>)}</nav>
      <button className="settings"><Settings size={18}/>Настройки</button>
    </aside>
    <main>
      <header><div><small>ФИНАНСЫ · КАДРЫ · ЗАРПЛАТА</small><h1>{active}</h1></div>
        <div className="header-right"><button className="icon-btn" onClick={refresh}><RefreshCw size={17}/></button><div className="period">Октябрь 2026</div></div>
      </header>
      {message&&<div className="toast">{message}</div>}
      {active==="Обзор"&&<Dashboard dash={dash} employees={employees} onGo={setActive}/>}
      {active==="Сотрудники"&&<Employees employees={employees} reload={load}/>}
      {active==="Зарплата"&&<Payroll onMessage={setMessage}/>}
      {active==="1С / Обмен"&&<Exchange onMessage={setMessage}/>}
      {active==="Календарь и табель"&&<Simple title="Календарь и табель" text="Производственный календарь, табель и контроль отклонений." icon={CalendarDays}/>}
      {active==="Кадры"&&<Simple title="Кадровый учёт" text="Приём, увольнение, отпуска, больничные и кадровые документы." icon={ShieldCheck}/>}
      {active==="Налоги"&&<Taxes onMessage={setMessage}/>}
      {active==="Отчёты"&&<Simple title="Отчёты" text="Зарплата, НДФЛ, взносы, стоимость персонала и годовые итоги." icon={FileSpreadsheet}/>}
      {active==="Помощник"&&<Simple title="AI-помощник бухгалтера" text="Контроль ошибок и ответы только на основании данных системы." icon={Bot}/>}
    </main>
  </div>
}

function Dashboard({dash,employees,onGo}:{dash:Dash|null;employees:Employee[];onGo:(x:string)=>void}){
  return <div className="grid">
    <section className="hero card"><div><small>ОКТЯБРЬ 2026</small><h2>Месяц под контролем</h2><p>Кадры, зарплата, налоги и обмен с 1С — в одном рабочем месте.</p></div><button className="primary" onClick={()=>onGo("Зарплата")}><Calculator size={17}/>Рассчитать зарплату</button></section>
    <Metric title="Сотрудники" value={String(dash?.employees??0)} note={dash?.payroll_ready?"данные заполнены":"нужно заполнить"} />
    <Metric title="Фонд окладов" value={money(dash?.active_salary??0)} note="до налогов" />
    <Metric title="Остаток отпуска" value={String(dash?.vacation_days??0)+" дн."} note="по активным сотрудникам" />
    <section className="card wide"><div className="section-head"><h3>Контроль месяца</h3><span className="status"><CheckCircle2 size={16}/> Система готова</span></div>
      <div className="checks"><span><CheckCircle2/> Сотрудники заведены</span><span><CheckCircle2/> История окладов</span><span><CircleAlert/> Табель перед расчётом</span><span><CircleAlert/> Закрытие месяца</span></div>
    </section>
    <section className="card wide"><div className="section-head"><h3>Сотрудники</h3><button className="link-btn" onClick={()=>onGo("Сотрудники")}>Все сотрудники →</button></div>
      {employees.length?<div className="table"><div className="tr th"><span>Сотрудник</span><span>Должность</span><span>Оклад</span><span>Отпуск</span></div>{employees.slice(0,5).map(e=><div className="tr" key={e.id}><span><b>{e.full_name}</b><small>{e.active?"Активен":"Уволен"}</small></span><span>{e.position}</span><span>{money(e.salary)}</span><span>{e.vacation_balance} дн.</span></div>)}</div>:<Empty text="Добавьте первого сотрудника"/>}
    </section>
  </div>
}
function Metric({title,value,note}:{title:string;value:string;note:string}){return <section className="card metric"><small>{title}</small><strong>{value}</strong><span>{note}</span></section>}
function Employees({employees,reload}:{employees:Employee[];reload:()=>void}){
  const [open,setOpen]=useState(false);
  return <div className="stack"><div className="toolbar"><div><h2>Сотрудники</h2><p>Кадровая база и история окладов.</p></div><button className="primary" onClick={()=>setOpen(true)}><Plus size={17}/>Добавить</button></div>
    <section className="card"><div className="table"><div className="tr th"><span>Сотрудник</span><span>Должность</span><span>Дата приёма</span><span>Оклад</span><span>Отпуск</span></div>
    {employees.map(e=><div className="tr" key={e.id}><span><b>{e.full_name}</b><small>{e.active?"Активен":"Уволен"}</small></span><span>{e.position}</span><span>{new Date(e.hire_date).toLocaleDateString("ru-RU")}</span><span>{money(e.salary)}</span><span>{e.vacation_balance} дн.</span></div>)}</div>{!employees.length&&<Empty text="Пока нет сотрудников"/>}</section>
    {open&&<EmployeeModal close={()=>setOpen(false)} reload={reload}/>}</div>
}
function EmployeeModal({close,reload}:{close:()=>void;reload:()=>void}){
  const [form,setForm]=useState({full_name:"",position:"Сотрудник",hire_date:"2026-10-01",salary:"",insurance_years:"0"});
  const [busy,setBusy]=useState(false);
  const save=async()=>{setBusy(true);const r=await fetch(API+"/employees",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({...form,salary:Number(form.salary),insurance_years:Number(form.insurance_years)})});setBusy(false);if(r.ok){close();reload()}};
  return <Modal title="Новый сотрудник" close={close}><div className="form"><label>ФИО<input value={form.full_name} onChange={e=>setForm({...form,full_name:e.target.value})}/></label><label>Должность<input value={form.position} onChange={e=>setForm({...form,position:e.target.value})}/></label><label>Дата приёма<input type="date" value={form.hire_date} onChange={e=>setForm({...form,hire_date:e.target.value})}/></label><label>Оклад, ₽<input type="number" value={form.salary} onChange={e=>setForm({...form,salary:e.target.value})}/></label><label>Страховой стаж, лет<input type="number" step=".1" value={form.insurance_years} onChange={e=>setForm({...form,insurance_years:e.target.value})}/></label><button className="primary full" disabled={busy} onClick={save}>{busy?"Сохранение…":"Сохранить сотрудника"}</button></div></Modal>
}
function Payroll({onMessage}:{onMessage:(x:string)=>void}){
  const [result,setResult]=useState<any>(null); const [busy,setBusy]=useState(false);
  const calculate=async()=>{setBusy(true);const r=await fetch(API+"/payroll/run?year=2026&month=10",{method:"POST"});const d=await r.json();setBusy(false);if(r.ok)setResult(d);else onMessage(d.detail||"Ошибка расчёта")};
  return <div className="stack"><div className="toolbar"><div><h2>Зарплата · Октябрь 2026</h2><p>Расчёт окладов, НДФЛ, взносов и полной стоимости работодателя.</p></div><button className="primary" onClick={calculate} disabled={busy}><Calculator size={17}/>{busy?"Считаем…":"Рассчитать"}</button></div>
    <section className="card"><div className="notice"><ShieldCheck size={18}/><div><b>Правила 2026</b><span>НДФЛ рассчитывается по прогрессивной шкале. Ставки и лимиты вынесены в расчётный модуль.</span></div></div>
    {result?<><div className="table payroll-table"><div className="tr th"><span>Сотрудник</span><span>Начислено</span><span>НДФЛ</span><span>К выплате</span><span>Взносы</span><span>Стоимость</span></div>{result.items.map((x:any)=><div className="tr" key={x.employee_id}><span><b>{x.name}</b></span><span>{money(Number(x.gross))}</span><span>{money(Number(x.ndfl))}</span><span>{money(Number(x.net))}</span><span>{money(Number(x.employer_contributions))}</span><span>{money(Number(x.employer_cost))}</span></div>)}</div><div className="result-footer"><b>Расчёт №{result.run_id}</b><span className="status"><CheckCircle2 size={16}/> Черновик — можно проверить и закрыть</span></div></>:<Empty text="Нажмите «Рассчитать», чтобы получить ведомость."/>}</section></div>
}

function Taxes({onMessage}:{onMessage:(x:string)=>void}){
  const [data,setData]=useState<any>(null); const [busy,setBusy]=useState(false);
  const load=async()=>{setBusy(true);const r=await fetch(API+"/taxes/usn?year=2026");const d=await r.json();setBusy(false);if(r.ok)setData(d);else onMessage(d.detail||"Ошибка расчёта УСН")};
  useEffect(()=>{load()},[]);
  return <div className="stack"><div className="toolbar"><div><h2>УСН · доходы минус расходы</h2><p>Нарастающим итогом с начала 2026 года. Ставка в системе — 15%.</p></div><button className="primary" onClick={load} disabled={busy}><Calculator size={17}/>{busy?"Считаем…":"Обновить расчёт"}</button></div>
    <div className="tax-grid"><Metric title="Доходы" value={money(Number(data?.income_ytd||0))} note="с начала года"/><Metric title="Расходы" value={money(Number(data?.expenses_ytd||0))} note="введены как расход"/><Metric title="Налоговая база" value={money(Number(data?.tax_base_ytd||0))} note="доходы − расходы"/><Metric title="УСН 15%" value={money(Number(data?.calculated_tax_ytd||0))} note="расчётная сумма"/></div>
    <section className="card"><div className="section-head"><h3>Контроль минимального налога</h3><span className="status"><ShieldCheck size={16}/> 1% от доходов</span></div><div className="tax-detail"><div><small>Минимальный налог</small><b>{money(Number(data?.minimum_tax_ytd||0))}</b></div><div><small>Авансы / платежи</small><b>{money(Number(data?.paid_advances||0))}</b></div><div><small>К доплате по текущему расчёту</small><b>{money(Number(data?.payment_due_ytd||0))}</b></div></div><p className="muted">Минимальный налог сравнивается с обычным налогом по итогам года. В течение года показатель показывается как контроль.</p></section>
  </div>
}

function Exchange({onMessage}:{onMessage:(x:string)=>void}){
 const [info,setInfo]=useState<any>(null); const [busy,setBusy]=useState(false);
 const upload=async(file:File)=>{setBusy(true);const fd=new FormData();fd.append("file",file);const r=await fetch(API+"/1c/inspect",{method:"POST",body:fd});const d=await r.json();setBusy(false);if(r.ok)setInfo(d);else onMessage(d.detail||"Ошибка архива")};
 const export1c=async()=>{const r=await fetch(API+"/1c/export?year=2026&month=10");if(!r.ok){onMessage((await r.json()).detail||"Сначала закройте месяц");return}const blob=await r.blob();const a=document.createElement("a");a.href=URL.createObjectURL(blob);a.download="laserlove-payroll-2026-10.xml";a.click();URL.revokeObjectURL(a.href)};
 return <div className="stack"><div className="toolbar"><div><h2>1С / Обмен</h2><p>Безопасный просмотр архивов и подготовка данных для обмена.</p></div><button className="secondary" onClick={export1c}><Download size={17}/>Выгрузить зарплату</button></div>
 <section className="card upload-card"><label className="drop"><Upload size={28}/><b>{busy?"Проверяем архив…":"Загрузить архив 1С"}</b><span>ZIP/XML · до 50 МБ · файлы не исполняются</span><input type="file" accept=".zip,.xml" onChange={e=>e.target.files?.[0]&&upload(e.target.files[0])}/></label>
 {info&&<div className="exchange-result"><div className="result-head"><div><b>Архив распознан</b><span>{info.files_count} файлов · {info.xml_count} XML</span></div><span className="status"><CheckCircle2 size={16}/> Можно переходить к сопоставлению</span></div><div className="mini-list">{(info.xml||[]).slice(0,8).map((x:any)=><div key={x.file}><span>{x.file}</span><small>{x.root||"XML ошибка"} · {x.size} байт</small></div>)}</div></div>}</section></div>
}
function Simple({title,text,icon:Icon}:{title:string;text:string;icon:any}){return <section className="card empty-page"><Icon size={32}/><h2>{title}</h2><p>{text}</p><div className="coming">Модуль в разработке — данные будут подключены к общей базе.</div></section>}
function Empty({text}:{text:string}){return <div className="empty"><CircleAlert size={20}/><span>{text}</span></div>}
function Modal({title,close,children}:{title:string;close:()=>void;children:React.ReactNode}){return <div className="overlay"><div className="modal"><div className="modal-head"><h3>{title}</h3><button className="icon-btn" onClick={close}><X size={18}/></button></div>{children}</div></div>}
createRoot(document.getElementById("root")!).render(<App/>);
