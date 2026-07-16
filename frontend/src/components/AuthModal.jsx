import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';
import { GoogleLogin } from '@react-oauth/google';

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
  const socialEnabled = googleId || fbId;

  return (
    <div className="modal-overlay open" onClick={onClose}>
      <div className="modal-panel" onClick={e => e.stopPropagation()} style={{ maxWidth: 460 }}>
        <h2>
          {user ? '👤 Minha Conta' : '👤 Entrar / Cadastrar'}
          <button onClick={onClose}>&times;</button>
        </h2>

        {user ? (
          <div>
            <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
              {['perfil', 'enderecos', 'favoritos'].map(t => (
                <button key={t} className={`auth-tab ${profileTab === t ? 'active' : ''}`}
                  onClick={() => setProfileTab(t)}
                  style={{ flex: 1, padding: '7px 4px', border: 'none', borderRadius: 6, background: profileTab === t ? '#e74c3c' : '#1a1a3e', color: '#fff', fontSize: 11, fontWeight: 600, cursor: 'pointer' }}>
                  {t === 'perfil' ? '👤 Perfil' : t === 'enderecos' ? '📍 Endereços' : '⭐ Favoritos'}
                </button>
              ))}
            </div>

            {profileTab === 'perfil' && (
              <div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" value={email} disabled style={{ opacity: 0.5 }} />
                </div>
                <div className="form-group">
                  <label>Nome</label>
                  <input type="text" value={nome} onChange={e => setNome(e.target.value)} placeholder="Seu nome" />
                </div>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button className="btn-auth-submit" onClick={handleUpdateProfile}>Salvar</button>
                  <button className="btn-auth-submit"
                    style={{ background: 'rgba(231,76,60,.5)', flex: 1 }} onClick={logout}>Sair</button>
                </div>
              </div>
            )}

            {profileTab === 'enderecos' && (
              <div>
                {enderecos.map(e => (
                  <div key={e.id} className="address-item">
                    <span className="addr-text">{e.endereco}</span>
                    <button onClick={() => handleRemoveEndereco(e.id)}>Remover</button>
                  </div>
                ))}
                {enderecos.length === 0 && (
                  <p style={{ fontSize: 12, color: '#888', textAlign: 'center', padding: 12 }}>Nenhum endereço salvo</p>
                )}
                <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                  <input type="text" value={novoEndereco} onChange={e => setNovoEndereco(e.target.value)}
                    placeholder="Novo endereço..." className="cust-input" />
                  <button className="btn-auth-submit" style={{ width: 'auto', padding: '8px 16px' }}
                    onClick={handleAddEndereco}>+</button>
                </div>
              </div>
            )}

            {profileTab === 'favoritos' && (
              <div>
                {favoritos.map(f => (
                  <div key={f.id} className="address-item">
                    <span className="addr-text">{f.nome || f.item_key}</span>
                    <button onClick={() => handleRemoveFav(f.id)}>&times;</button>
                  </div>
                ))}
                {favoritos.length === 0 && (
                  <p style={{ fontSize: 12, color: '#888', textAlign: 'center', padding: 12 }}>Nenhum favorito ainda</p>
                )}
              </div>
            )}
          </div>
        ) : (
          <div>
            <div className="auth-tabs">
              <button className={`auth-tab ${tab === 'entrar' ? 'active' : ''}`}
                onClick={() => setTab('entrar')}>Entrar</button>
              <button className={`auth-tab ${tab === 'cadastrar' ? 'active' : ''}`}
                onClick={() => setTab('cadastrar')}>Cadastrar</button>
            </div>

            <form onSubmit={handleSubmit}>
              {tab === 'cadastrar' && (
                <div className="form-group">
                  <label>Nome</label>
                  <input type="text" value={nome} onChange={e => setNome(e.target.value)}
                    placeholder="Seu nome" required />
                </div>
              )}
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="seu@email.com" required />
              </div>
              <div className="form-group">
                <label>Senha</label>
                <input type="password" value={senha} onChange={e => setSenha(e.target.value)}
                  placeholder="Mínimo 6 caracteres" minLength={6} required />
              </div>
              <button className="btn-auth-submit" type="submit" disabled={loading}>
                {loading ? 'Aguarde...' : tab === 'entrar' ? 'Entrar' : 'Cadastrar'}
              </button>
            </form>

            {socialEnabled && (
              <>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, margin: '14px 0' }}>
                  <div style={{ flex: 1, height: 1, background: '#2a2a5e' }}></div>
                  <span style={{ fontSize: 11, color: '#666' }}>ou</span>
                  <div style={{ flex: 1, height: 1, background: '#2a2a5e' }}></div>
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {googleId && (
                    <div style={{ display: 'flex', justifyContent: 'center' }}>
                      <GoogleLogin
                        onSuccess={handleGoogleSuccess}
                        onError={() => onToast('Erro no login Google', 'error')}
                        theme="filled_black"
                        size="large"
                        shape="pill"
                        text="signin_with"
                        logo_alignment="center"
                      />
                    </div>
                  )}
                  {fbId && (
                    <button onClick={handleFacebookLogin}
                      style={{
                        display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                        padding: '10px 16px', border: 'none', borderRadius: 24,
                        background: '#1877f2', color: '#fff', fontSize: 14, fontWeight: 600,
                        cursor: 'pointer', width: '100%'
                      }}>
                      <span style={{ fontSize: 18 }}>f</span> Entrar com Facebook
                    </button>
                  )}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
