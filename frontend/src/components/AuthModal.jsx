import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';
import { useGoogleLogin } from '@react-oauth/google';

const dividerStyle = {
  display: 'flex', alignItems: 'center', gap: 12, margin: '16px 0',
};

const dividerLine = {
  flex: 1, height: 1, background: 'linear-gradient(90deg, transparent, #2a2a5e, transparent)',
};

export default function AuthModal({ open, onClose, onToast }) {
  const { user, login, register, logout, updateUser } = useAuth();
  const [tab, setTab] = useState('entrar');
  const [email, setEmail] = useState('');
  const [senha, setSenha] = useState('');
  const [nome, setNome] = useState('');
  const [loading, setLoading] = useState(false);
  const [enderecos, setEnderecos] = useState([]);
  const [novoEndereco, setNovoEndereco] = useState('');
  const [favoritos, setFavoritos] = useState([]);
  const [profileTab, setProfileTab] = useState('perfil');

  useEffect(() => {
    if (open && user) {
      setNome(user.nome || '');
      setEmail(user.email || '');
      api.enderecos.listar().then(d => setEnderecos(d.enderecos || [])).catch(() => {});
      api.favoritos.listar().then(d => setFavoritos(d.favoritos || [])).catch(() => {});
    }
  }, [open, user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      if (tab === 'entrar') {
        await login(email, senha);
        onToast('Login realizado!', 'success');
      } else {
        await register(email, senha, nome);
        onToast('Conta criada!', 'success');
      }
    } catch (err) { onToast(err.message, 'error'); }
    setLoading(false);
  };

  const handleGoogleSuccess = useCallback(async (credentialResponse) => {
    try {
      const data = await api.auth.googleLogin(credentialResponse.credential);
      localStorage.setItem('token', data.token);
      window.location.reload();
    } catch (err) { onToast(err.message, 'error'); }
  }, [onToast]);

  const googleLogin = useGoogleLogin({
    onSuccess: handleGoogleSuccess,
    onError: () => onToast('Erro no login Google', 'error'),
    flow: 'implicit',
  });

  const handleFacebookLogin = useCallback(() => {
    if (!window.FB) { onToast('Facebook SDK não carregado', 'error'); return; }
    window.FB.login(async (response) => {
      if (response.authResponse) {
        try {
          const data = await api.auth.facebookLogin(response.authResponse.accessToken);
          localStorage.setItem('token', data.token);
          window.location.reload();
        } catch (err) { onToast(err.message, 'error'); }
      } else {
        onToast('Login do Facebook cancelado', 'error');
      }
    }, { scope: 'public_profile,email' });
  }, [onToast]);

  const handleAddEndereco = async () => {
    if (!novoEndereco.trim()) return;
    try {
      const d = await api.enderecos.adicionar({ endereco: novoEndereco.trim() });
      setEnderecos(prev => [...prev, d.endereco]);
      setNovoEndereco('');
      onToast('Endereço salvo!', 'success');
    } catch (err) { onToast(err.message, 'error'); }
  };

  const handleRemoveEndereco = async (id) => {
    try { await api.enderecos.remover(id); setEnderecos(prev => prev.filter(e => e.id !== id)); }
    catch (err) { onToast(err.message, 'error'); }
  };

  const handleRemoveFav = async (id) => {
    try { await api.favoritos.remover(id); setFavoritos(prev => prev.filter(f => f.id !== id)); }
    catch (err) { onToast(err.message, 'error'); }
  };

  const handleUpdateProfile = async () => {
    try { await updateUser({ nome }); onToast('Perfil atualizado!', 'success'); }
    catch (err) { onToast(err.message, 'error'); }
  };

  if (!open) return null;

  const googleId = window.__GOOGLE_CLIENT_ID;
  const fbId = window.__FB_APP_ID;

  if (user) {
    return (
      <div className="modal-overlay open" onClick={onClose}>
        <div className="modal-panel" onClick={e => e.stopPropagation()} style={{ maxWidth: 460 }}>
          <div style={modalHeaderStyle}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <div style={avatarStyle}>{user.nome ? user.nome[0].toUpperCase() : '👤'}</div>
              <div>
                <div style={{ fontSize: 15, fontWeight: 700, color: '#fff' }}>{user.nome || 'Usuário'}</div>
                <div style={{ fontSize: 11, color: '#888' }}>{user.email}</div>
              </div>
            </div>
            <button onClick={onClose} style={closeBtnStyle}>&times;</button>
          </div>

          <div style={profileNavStyle}>
            {[
              { id: 'perfil', icon: '👤', label: 'Perfil' },
              { id: 'enderecos', icon: '📍', label: 'Endereços', count: enderecos.length },
              { id: 'favoritos', icon: '⭐', label: 'Favoritos', count: favoritos.length },
            ].map(t => (
              <button key={t.id} onClick={() => setProfileTab(t.id)}
                style={{
                  ...profileNavBtnStyle,
                  background: profileTab === t.id ? 'linear-gradient(135deg,#e74c3c,#c0392b)' : '#1a1a3e',
                  borderColor: profileTab === t.id ? 'transparent' : '#2a2a5e',
                }}>
                <span style={{ fontSize: 16 }}>{t.icon}</span>
                <span style={{ fontSize: 11, fontWeight: 600 }}>{t.label}</span>
                {t.count > 0 && <span style={badgeStyle}>{t.count}</span>}
              </button>
            ))}
          </div>

          {profileTab === 'perfil' && (
            <div>
              <div style={sectionCardStyle}>
                <div className="form-group">
                  <label style={{ fontSize: 11, color: '#888', display: 'block', marginBottom: 4 }}>📧 Email</label>
                  <input type="email" value={email} disabled style={inputDisabledStyle} />
                </div>
                <div className="form-group" style={{ marginTop: 10 }}>
                  <label style={{ fontSize: 11, color: '#888', display: 'block', marginBottom: 4 }}>👤 Nome</label>
                  <input type="text" value={nome} onChange={e => setNome(e.target.value)}
                    placeholder="Seu nome" style={inputStyle} />
                </div>
              </div>
              <div style={{ display: 'flex', gap: 8, marginTop: 12 }}>
                <button onClick={handleUpdateProfile} style={primaryBtnStyle}>
                  {loading ? '⏳ Salvando...' : '💾 Salvar'}
                </button>
                <button onClick={logout} style={{ ...dangerBtnStyle }}>🚪 Sair</button>
              </div>
            </div>
          )}

          {profileTab === 'enderecos' && (
            <div>
              {enderecos.length === 0 ? (
                <div style={emptyStateStyle}>
                  <div style={{ fontSize: 32, marginBottom: 6 }}>📍</div>
                  <div style={{ fontSize: 13, color: '#888' }}>Nenhum endereço salvo</div>
                  <div style={{ fontSize: 11, color: '#555', marginTop: 4 }}>Adicione endereços para agilizar seus pedidos</div>
                </div>
              ) : (
                enderecos.map(e => (
                  <div key={e.id} style={addressCardStyle}>
                    <div style={{ fontSize: 16, marginRight: 8 }}>📍</div>
                    <span style={{ flex: 1, fontSize: 13, color: '#ccc' }}>{e.endereco}</span>
                    <button onClick={() => handleRemoveEndereco(e.id)} style={smallRemoveBtnStyle}>✕</button>
                  </div>
                ))
              )}
              <div style={{ display: 'flex', gap: 6, marginTop: 10 }}>
                <input type="text" value={novoEndereco} onChange={e => setNovoEndereco(e.target.value)}
                  placeholder="Rua, número, bairro..." style={inputStyle} />
                <button onClick={handleAddEndereco}
                  style={{ ...primaryBtnStyle, width: 'auto', padding: '10px 18px', fontSize: 18 }}>+</button>
              </div>
            </div>
          )}

          {profileTab === 'favoritos' && (
            <div>
              {favoritos.length === 0 ? (
                <div style={emptyStateStyle}>
                  <div style={{ fontSize: 32, marginBottom: 6 }}>⭐</div>
                  <div style={{ fontSize: 13, color: '#888' }}>Nenhum favorito ainda</div>
                  <div style={{ fontSize: 11, color: '#555', marginTop: 4 }}>
                    Favorite pizzas tocando na ☆ ao lado do nome
                  </div>
                </div>
              ) : (
                favoritos.map(f => (
                  <div key={f.id} style={addressCardStyle}>
                    <div style={{ fontSize: 16, marginRight: 8 }}>⭐</div>
                    <span style={{ flex: 1, fontSize: 13, color: '#ccc' }}>{f.nome || f.item_key}</span>
                    <button onClick={() => handleRemoveFav(f.id)} style={smallRemoveBtnStyle}>✕</button>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>
    );
  }

  return (
    <div className="modal-overlay open" onClick={onClose}>
      <div className="modal-panel" onClick={e => e.stopPropagation()} style={{ maxWidth: 420 }}>
        <div style={modalHeaderStyle}>
          <span style={{ fontSize: 16, fontWeight: 700, color: '#fff' }}>👤 Entrar / Cadastrar</span>
          <button onClick={onClose} style={closeBtnStyle}>&times;</button>
        </div>

        <div style={{ display: 'flex', gap: 0, marginBottom: 16, borderRadius: 10, overflow: 'hidden', border: '1px solid #2a2a5e' }}>
          {['entrar', 'cadastrar'].map(t => (
            <button key={t} onClick={() => setTab(t)}
              style={{
                flex: 1, padding: '11px 0', border: 'none',
                background: tab === t ? 'linear-gradient(135deg,#e74c3c,#c0392b)' : '#0f0f23',
                color: tab === t ? '#fff' : '#666', fontSize: 13, fontWeight: 600, cursor: 'pointer',
                transition: 'all .2s',
              }}>
              {t === 'entrar' ? '🔑 Entrar' : '📝 Cadastrar'}
            </button>
          ))}
        </div>

        {(googleId || fbId) && (
          <div className="social-btn-wrapper">
            {fbId && (
              <button onClick={handleFacebookLogin} className="social-btn social-btn-facebook">
                <svg width="20" height="20" viewBox="0 0 40 40" fill="none">
                  <path d="M20 0C8.954 0 0 8.954 0 20c0 9.986 7.314 18.258 16.875 19.758V25.78h-5.078V20h5.078v-4.41c0-5.012 2.985-7.78 7.552-7.78 2.188 0 4.477.39 4.477.39v4.922h-2.522c-2.484 0-3.257 1.54-3.257 3.12V20h5.547l-.887 5.78h-4.66v14.258C32.686 38.258 40 29.986 40 20 40 8.954 31.046 0 20 0z" fill="#fff"/>
                </svg>
                Entrar com Facebook
              </button>
            )}
            {googleId && (
              <button onClick={() => googleLogin()} className="social-btn social-btn-google">
                <svg width="20" height="20" viewBox="0 0 48 48">
                  <path fill="#4285F4" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.72 17.74 9.5 24 9.5z"/>
                  <path fill="#34A853" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/>
                  <path fill="#FBBC05" d="M10.54 28.59A14.5 14.5 0 019.5 24c0-1.59.28-3.14.76-4.59l-7.98-6.19A23.99 23.99 0 000 24c0 3.77.87 7.35 2.56 10.56l7.98-5.97z"/>
                  <path fill="#EA4335" d="M24 48c6.48 0 11.93-2.13 15.89-5.76l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 5.97C6.51 42.62 14.62 48 24 48z"/>
                </svg>
                Entrar com Google
              </button>
            )}
          </div>
        )}

        {(googleId || fbId) && (
          <div style={dividerStyle}>
            <div style={dividerLine}></div>
            <span style={{ fontSize: 12, color: '#555', fontWeight: 600 }}>ou com email</span>
            <div style={dividerLine}></div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {tab === 'cadastrar' && (
            <div className="form-group" style={{ marginBottom: 10 }}>
              <label style={{ fontSize: 11, color: '#888', display: 'block', marginBottom: 4 }}>👤 Nome</label>
              <input type="text" value={nome} onChange={e => setNome(e.target.value)}
                placeholder="Seu nome completo" required style={inputStyle} />
            </div>
          )}
          <div className="form-group" style={{ marginBottom: 10 }}>
            <label style={{ fontSize: 11, color: '#888', display: 'block', marginBottom: 4 }}>📧 Email</label>
            <input type="email" value={email} onChange={e => setEmail(e.target.value)}
              placeholder="seu@email.com" required style={inputStyle} />
          </div>
          <div className="form-group" style={{ marginBottom: tab === 'entrar' ? 10 : 14 }}>
            <label style={{ fontSize: 11, color: '#888', display: 'block', marginBottom: 4 }}>🔒 Senha</label>
            <input type="password" value={senha} onChange={e => setSenha(e.target.value)}
              placeholder={tab === 'entrar' ? 'Sua senha' : 'Mínimo 6 caracteres'} minLength={6} required style={inputStyle} />
          </div>
          <button type="submit" disabled={loading}
            style={{
              ...primaryBtnStyle,
              opacity: loading ? 0.6 : 1,
              cursor: loading ? 'not-allowed' : 'pointer',
            }}>
            {loading ? (
              <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                <span style={spinnerStyle}></span>
                Aguarde...
              </span>
            ) : (
              tab === 'entrar' ? '🔑 Entrar' : '📝 Criar Conta'
            )}
          </button>
        </form>

        {tab === 'entrar' && (
          <p style={{ textAlign: 'center', fontSize: 11, color: '#555', marginTop: 12 }}>
            Ao entrar, você concorda com nossos Termos de Uso
          </p>
        )}
      </div>
    </div>
  );
}

const modalHeaderStyle = {
  display: 'flex', justifyContent: 'space-between', alignItems: 'center',
  marginBottom: 16, paddingBottom: 12,
  borderBottom: '1px solid rgba(255,255,255,.06)',
};

const closeBtnStyle = {
  background: 'rgba(231,76,60,.12)', border: 'none', color: '#e74c3c',
  fontSize: 20, width: 30, height: 30, borderRadius: '50%', cursor: 'pointer',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  transition: 'all .2s',
};

const inputStyle = {
  width: '100%', padding: '10px 12px', borderRadius: 8,
  border: '1px solid #2a2a5e', background: '#0f0f23',
  color: '#eee', fontSize: 13, outline: 'none', boxSizing: 'border-box',
  transition: 'border .15s',
};

const inputDisabledStyle = {
  ...inputStyle, opacity: 0.4, cursor: 'not-allowed',
};

const primaryBtnStyle = {
  flex: 1, padding: '11px 0', border: 'none', borderRadius: 8,
  background: 'linear-gradient(135deg,#e74c3c,#c0392b)', color: '#fff',
  fontSize: 13, fontWeight: 700, cursor: 'pointer', transition: 'all .2s',
};

const dangerBtnStyle = {
  padding: '11px 18px', border: '1px solid rgba(231,76,60,.3)', borderRadius: 8,
  background: 'rgba(231,76,60,.08)', color: '#e74c3c',
  fontSize: 13, fontWeight: 600, cursor: 'pointer', transition: 'all .2s',
};

const avatarStyle = {
  width: 38, height: 38, borderRadius: '50%',
  background: 'linear-gradient(135deg,#e74c3c,#c0392b)',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  fontSize: 16, fontWeight: 700, color: '#fff', flexShrink: 0,
};

const profileNavStyle = {
  display: 'flex', gap: 6, marginBottom: 14,
};

const profileNavBtnStyle = {
  flex: 1, padding: '8px 4px', border: '1px solid #2a2a5e', borderRadius: 8,
  color: '#fff', cursor: 'pointer', display: 'flex', flexDirection: 'column',
  alignItems: 'center', gap: 3, transition: 'all .2s', fontSize: 11,
};

const badgeStyle = {
  background: 'rgba(231,76,60,.25)', color: '#e74c3c',
  fontSize: 9, fontWeight: 700, padding: '1px 6px', borderRadius: 8,
};

const sectionCardStyle = {
  background: 'rgba(0,0,0,.15)', borderRadius: 10, padding: 12,
  border: '1px solid rgba(255,255,255,.04)',
};

const addressCardStyle = {
  display: 'flex', alignItems: 'center', padding: '8px 10px',
  background: 'rgba(0,0,0,.12)', borderRadius: 8, marginBottom: 4,
  border: '1px solid rgba(255,255,255,.04)',
};

const smallRemoveBtnStyle = {
  background: 'rgba(231,76,60,.12)', border: 'none', color: '#e74c3c',
  cursor: 'pointer', width: 24, height: 24, borderRadius: '50%',
  display: 'flex', alignItems: 'center', justifyContent: 'center',
  fontSize: 11, flexShrink: 0, transition: 'all .15s',
};

const emptyStateStyle = {
  textAlign: 'center', padding: '24px 12px',
};

const spinnerStyle = {
  width: 14, height: 14, border: '2px solid rgba(255,255,255,.3)',
  borderTopColor: '#fff', borderRadius: '50%',
  animation: 'spin .8s linear infinite', display: 'inline-block',
};
