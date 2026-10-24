"""Line breaks for the two-column IEEE Open Journals measure."""
import re

def wrap_equations(t):
    replacements={
    'eq:ageaggregate':r'''\begin{aligned}
 B_{is}(t)&=\sum_{a\ge0}X_{isa}(t),\quad S_{is}(t)=\sum_{a\ge0}Y_{isa}(t),\\
 0&\le Y_{isa}(t)\le X_{isa}(t).
\end{aligned}''',
    'eq:agemiss':r'''\begin{aligned}
 V_s&=1-\frac1{N_s}\sum_{t=0}^{T-1}\sum_{a=0}^{D_s-1}\chi(t,a)Y_{3sa}(t),\\
 N_s&=\sum_{t=b_{\min}}^{b_{\max}-1}A_s(t).
\end{aligned}''',
    'eq:activecommand':r'''\begin{aligned}
 k^*(t)&=\underset{k:d_k\le t}{\arg\max}_{\rm lex}(d_k,k),\\
 e(t)&=x_{k^*(t)},\qquad W(t)=W_{k^*(t)}.
\end{aligned}''',
    'eq:miss':r'''V_s=\frac{N_s^{\rm late}+N_s^{\rm unfinished}}{\max(1,N_s)}.''',
    'eq:project':r'''\begin{aligned}
 \widehat q_{is}(u+1)&=\left[\widehat q_{is}(u)\right.\\[-2pt]
 &\quad\left.-F_s\bigl(\widehat q_i(u),w_i(u),\bar c_i+e_i(u)\bigr)\right]^+
 +\bar a_{is},\\
 &\qquad u=\tau_i,\ldots,t+L-1.
\end{aligned}''',
    'eq:feasibleset':r'''\begin{gathered}
 \rho_s=H_s/(\eta D_s),\\
 \mathcal F(\eta)=\{(x,\alpha)\in\mathcal X:\rho_s\le1\ \forall s\}.
\end{gathered}''',
    'eq:integerquota':r'''\begin{aligned}
 g_0(C,\alpha)&=\lfloor r_0\rfloor+\nu\mathbf1\{f_0\ge f_1\},\\
 g_1(C,\alpha)&=C-g_0(C,\alpha).
\end{aligned}''',
    'eq:calibration':r'''\begin{aligned}
 \theta_m^*&=\arg\min_{\theta\in\Theta_m}\overline J_{m\theta}\\
 &\text{subject to }U_{m\theta cs}\le\epsilon\quad\forall c,s,\\
 &\epsilon=10^{-3}.
\end{aligned}''',
    'eq:hpa':r'''\begin{aligned}
 b_i(t)&=\left[\left\lceil\frac{\sum_s\bar a_{is}+\sum_s q_{is}/h}{u}\right\rceil-\bar c_i\right]_0^3,\\
 x_i(t)&=\max_{v\in\mathcal H_t}b_i(v).
\end{aligned}''',
    'eq:costdecomposition':r'''\begin{aligned}
 J&=J_{\mathrm{cap}}+J_{\mathrm{sw}},\qquad J_{\mathrm{cap}}=\sum_{t,i}e_i(t),\\
 J_{\mathrm{sw}}&=\kappa\sum_{a\in\mathcal A_T}\|x_a-e_a^-\|_1.
\end{aligned}''',
    }
    def sub(m):
        labels=re.findall(r'\\label\{([^}]+)\}',m[0])
        for label in labels:
            if label in replacements:
                return '\\begin{equation}\n'+replacements[label]+'\n\\label{'+label+'}\n\\end{equation}'
        return m[0]
    t=re.sub(r'\\begin\{equation\}.*?\\end\{equation\}',sub,t,flags=re.S)
    t=t.replace('The tail extends beyond all measured deadlines,',r'Here $N_s^{\rm late}$ counts completed cohort packets with $\ell_p>D_s$, and $N_s^{\rm unfinished}$ counts cohort packets unfinished at run end. The tail extends beyond all measured deadlines,')
    t=t.replace(r'u_{is}=\min\{B_{is},g_{is}\},\qquad'+'\n'+r' B_{1s}=Q_{1s}+A_s,\quad B_{is}=Q_{is}\ (i>1).',r'\begin{gathered}u_{is}=\min\{B_{is},g_{is}\},\\B_{1s}=Q_{1s}+A_s,\quad B_{is}=Q_{is}\ (i>1).\end{gathered}')
    t=t.replace(r'X_{1s,0}(t+1)&=A_s(t+1),&X_{is,0}(t+1)&=0\quad(i>1),',r'X_{1s,0}(t+1)&=A_s(t+1),\nonumber\\X_{is,0}(t+1)&=0\quad(i>1),')
    t=t.replace(r'X_{is,a+1}(t+1)&=X_{isa}(t)-Y_{isa}(t)+Y_{i-1,s,a}(t),'+ '\n'+r' \quad i=2,3.',r'X_{is,a+1}(t+1)&=X_{isa}(t)-Y_{isa}(t)\nonumber\\&\quad+Y_{i-1,s,a}(t),\quad i=2,3.')
    t=t.replace(r'\mathcal X=\{(x,\alpha):x=(0,x_2,x_3),\ x_2,x_3\in\{0,1,2,3\},'+ '\n'+r' \ \alpha=k/20,\ k=1,\ldots,19\},\quad |\mathcal X|=304.',r'\begin{gathered}\mathcal X=\{((0,x_2,x_3),k/20):\\ x_2,x_3\in\{0,1,2,3\},\ k\in\{1,\ldots,19\}\},\\|\mathcal X|=304.\end{gathered}')
    return t
