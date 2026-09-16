import os,random,sqlite3
from pathlib import Path
import discord
from discord.ext import commands
RATE=.003
# 기록 DB는 Railway Volume(/data)에 저장합니다.
# DATA_DIR이 있으면 그 값을 우선 사용하고, 없더라도 /data가 존재하면 자동 사용합니다.
_data_env = os.getenv("DATA_DIR")
if _data_env:
 D = Path(_data_env)
elif Path("/data").exists():
 D = Path("/data")
else:
 D = Path(".")
D.mkdir(parents=True,exist_ok=True)
DB=D/"epinea.db"
TOKEN=os.getenv("DISCORD_BOT_TOKEN") or os.getenv("DISCORD_TOKEN")
if not TOKEN: raise RuntimeError("DISCORD_BOT_TOKEN을 등록해주세요.")
def cx():
 c=sqlite3.connect(DB);c.row_factory=sqlite3.Row;return c
def init():
 with cx() as c:
  c.execute("CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY,name TEXT,kills INTEGER DEFAULT 0,rings INTEGER DEFAULT 0)")
  c.execute("CREATE TABLE IF NOT EXISTS rings(n INTEGER PRIMARY KEY AUTOINCREMENT,uid INTEGER,s INTEGER,d INTEGER,i INTEGER,l INTEGER,a INTEGER,m INTEGER)")
def user(u):
 with cx() as c:
  c.execute("INSERT INTO users(id,name) VALUES(?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name",(u.id,u.display_name));c.commit()
  return c.execute("SELECT * FROM users WHERE id=?",(u.id,)).fetchone()
def hunt(u,n):
 rs=[]
 for _ in range(n):
  if random.random()<RATE: rs.append([7+random.randint(-1,1) for x in range(4)]+[3+random.randint(-1,1) for x in range(2)])
 with cx() as c:
  c.execute("INSERT INTO users(id,name,kills,rings) VALUES(?,?,?,?) ON CONFLICT(id) DO UPDATE SET name=excluded.name,kills=users.kills+excluded.kills,rings=users.rings+excluded.rings",(u.id,u.display_name,n,len(rs)))
  for r in rs:c.execute("INSERT INTO rings(uid,s,d,i,l,a,m) VALUES(?,?,?,?,?,?,?)",(u.id,*r))
  c.commit(); row=c.execute("SELECT * FROM users WHERE id=?",(u.id,)).fetchone()
 return rs,row
def emb(u,r,n=None,rs=None):
 e=discord.Embed(title="🦋 에피네아 반지 드랍",description=f"{u.mention}님의 누적 기록",color=0xd96ad9)
 if n is not None:e.add_field(name=f"⚔️ {n}마리 결과",value=(f"🎉 반지 **{len(rs)}개** 획득!" if rs else "💨 반지 없음"),inline=False)
 e.add_field(name="총 처치",value=f"**{r['kills']:,}마리**");e.add_field(name="반지",value=f"**{r['rings']}개**");e.add_field(name="확률",value="**0.3%**")
 e.set_image(url="attachment://epinea.png");e.set_footer(text="초기화 전까지 자동 저장됩니다.");return e
class V(discord.ui.View):
 def __init__(self,uid):super().__init__(timeout=600);self.uid=uid
 async def interaction_check(self,x):
  if x.user.id!=self.uid:await x.response.send_message("본인 사냥창을 열어주세요.",ephemeral=True);return False
  return True
 async def go(self,x,n):
  await x.response.defer();rs,r=hunt(x.user,n);f=discord.File("epinea.png",filename="epinea.png")
  await x.edit_original_response(embed=emb(x.user,r,n,rs),attachments=[f],view=self)
  for z in rs:
   q=discord.Embed(title="💍 에피네아의 반지 획득!",description=f"**STR : +{z[0]}**\n**DEX : +{z[1]}**\n**INT : +{z[2]}**\n**LUK : +{z[3]}**\n**공격력 : +{z[4]}**\n**마력 : +{z[5]}**",color=0xd96ad9)
   q.set_image(url="attachment://ring.png");await x.followup.send(embed=q,file=discord.File("ring.png",filename="ring.png"),ephemeral=True)
 @discord.ui.button(label="1마리 잡기",style=discord.ButtonStyle.secondary)
 async def a(self,x,b):await self.go(x,1)
 @discord.ui.button(label="5마리 잡기",style=discord.ButtonStyle.primary)
 async def b(self,x,b):await self.go(x,5)
 @discord.ui.button(label="10마리 잡기",style=discord.ButtonStyle.success)
 async def c(self,x,b):await self.go(x,10)
 @discord.ui.button(label="초기화",style=discord.ButtonStyle.danger)
 async def d(self,x,b):
  with cx() as c:c.execute("DELETE FROM rings WHERE uid=?",(x.user.id,));c.execute("UPDATE users SET kills=0,rings=0 WHERE id=?",(x.user.id,));c.commit()
  await x.response.send_message("🔄 초기화 완료",ephemeral=True)
class B(commands.Bot):
 def __init__(self):super().__init__(command_prefix="!",intents=discord.Intents.default())
 async def setup_hook(self):
  init();print(f"에피반지 DB 저장 위치: {DB.resolve()}");await self.tree.sync()
bot=B()
@bot.tree.command(name="에피반지",description="에피네아를 잡아 반지를 먹습니다.")
async def main(x):
 await x.response.defer();r=user(x.user);await x.edit_original_response(embed=emb(x.user,r),attachments=[discord.File("epinea.png",filename="epinea.png")],view=V(x.user.id))
@bot.tree.command(name="에피보기",description="내 에피네아 기록을 봅니다.")
async def see(x):
 r=user(x.user)
 with cx() as c:rs=c.execute("SELECT * FROM rings WHERE uid=? ORDER BY n DESC LIMIT 10",(x.user.id,)).fetchall()
 t=f"총 처치 **{r['kills']:,}마리** / 반지 **{r['rings']}개**"
 for j,z in enumerate(rs,1):t+=f"\n`{j}.` 힘 {z['s']} 덱 {z['d']} 인트 {z['i']} 럭 {z['l']} 공 {z['a']} 마 {z['m']}"
 await x.response.send_message(embed=discord.Embed(title="📊 내 기록",description=t),ephemeral=True)
@bot.tree.command(name="에피랭킹",description="반지 획득 랭킹")
async def rank(x):
 with cx() as c:rs=c.execute("SELECT * FROM users ORDER BY rings DESC,kills ASC LIMIT 10").fetchall()
 t="\n".join(f"**{j}. {z['name']}** — 반지 **{z['rings']}개** / {z['kills']:,}마리" for j,z in enumerate(rs,1)) or "기록 없음"
 await x.response.send_message(embed=discord.Embed(title="🏆 에피네아 반지 랭킹",description=t))
@bot.tree.command(name="에피초기화",description="내 기록 초기화")
async def reset(x):
 with cx() as c:c.execute("DELETE FROM rings WHERE uid=?",(x.user.id,));c.execute("UPDATE users SET kills=0,rings=0 WHERE id=?",(x.user.id,));c.commit()
 await x.response.send_message("🔄 초기화 완료",ephemeral=True)
bot.run(TOKEN)
