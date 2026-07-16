import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../api';

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

  useEffect(() => {
    if (open && user) {
      api.enderecos.listar().then(d => setEnderecos(d.enderecos || [])).catch(() => {});
      api.favoritos.listar().then(d => setFavoritos(d.favoritos || [])).catch(() => {});
    }
    if (open && user) {
      setNome(user.nome || '');
      setEmail(user.email || '');
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
    } catch (err) {
      onToast(err.message, 'error');
    }
    setLoading(false);
  };

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
    try {
      await api.enderecos.remover(id);
      setEnderecos(prev => prev.filter(e => e.id !== id));
    } catch (err) { onToast(err.message, 'error'); }
  };

  const handleRemoveFav = async (id) => {
    try {
      await api.favoritos.remover(id);
      setFavoritos(prev => prev.filter(f => f.id !== id));
    } catch (err) { onToast(err.message, 'error'); }
  };

  const handleUpdateProfile = async () => {
    try {
      await updateUser({ nome });
      onToast('Perfil atualizado!', 'success');
    } catch (err) { onToast(err.message, 'error'); }
  };

  if (!open) return null;

  return (
    <div className="modal-overlay open" onClick={onClose}>
      <div className="modal-panel" onClick={e => e.stopPropagation()} style={{ maxWidth: 460 }}>
        <h2>{user ? '👤 Minha Conta' : '👤 Entrar / Cadastrar'} <button onClick={onClose}>&times;</button></h2>

        {user ? (
          <div>
            <div className="auth-tabs">
              <button className={`auth-tab ${tab === 'perfil' ? 'active' : ''}`}
                onClick={() => setTab('perfil')}>Perfil</button>
              <button className={`auth-tab ${tab === 'enderecos' ? 'active' : ''}`}
                onClick={() => setTab('enderecos')}>Endereços</button>
              <button className={`auth-tab ${tab === 'favoritos' ? 'active' : ''}`}
                onClick={() => setTab('favoritos')}>Favoritos</button>
            </div>

            {tab === 'perfil' && (
              <div style={{ padding: 8 }}>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" value={email} disabled style={{ opacity: 0.5 }} />
                </div>
                <div className="form-group">
                  <label>Nome</label>
                  <input type="text" value={nome} onChange={e => setNome(e.target.value)} placeholder="Seu nome" />
                </div>
                <button className="btn-auth-submit" onClick={handleUpdateProfile}>Salvar</button>
                <button className="btn-auth-submit" style={{ background: 'rgba(231,76,60,.5)', marginTop: 8 }} onClick={logout}>Sair</button>
              </div>
            )}

            {tab === 'enderecos' && (
              <div style={{ padding: 8 }}>
                {enderecos.map(e => (
                  <div key={e.id} className="address-item">
                    <span className="addr-text">{e.endereco}</span>
                    <button onClick={() => handleRemoveEndereco(e.id)}>Remover</button>
                  </div>
                ))}
                {enderecos.length === 0 && <p style={{ fontSize: 12, color: '#888', textAlign: 'center', padding: 12 }}>Nenhum endereço salvo</p>}
                <div style={{ display: 'flex', gap: 6, marginTop: 8 }}>
                  <input type="text" value={novoEndereco} onChange={e => setNovoEndereco(e.target.value)}
                    placeholder="Novo endereço..." style={{ flex: 1, padding: 8, borderRadius: 6, border: '1px solid #2a2a5e', background: '#0f0f23', color: '#eee', fontSize: 12 }} />
                  <button className="btn-auth-submit" style={{ width: 'auto', padding: '8px 16px' }} onClick={handleAddEndereco}>+</button>
                </div>
              </div>
            )}

            {tab === 'favoritos' && (
              <div style={{ padding: 8 }}>
                {favoritos.map(f => (
                  <div key={f.id} className="address-item">
                    <span className="addr-text">{f.nome || f.item_key}</span>
                    <button onClick={() => handleRemoveFav(f.id)}>&times;</button>
                  </div>
                ))}
                {favoritos.length === 0 && <p style={{ fontSize: 12, color: '#888', textAlign: 'center', padding: 12 }}>Nenhum favorito ainda</p>}
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

            <form onSubmit={handleSubmit} style={{ padding: 4 }}>
              {tab === 'cadastrar' && (
                <div className="form-group">
                  <label>Nome</label>
                  <input type="text" value={nome} onChange={e => setNome(e.target.value)} placeholder="Seu nome" required />
                </div>
              )}
              <div className="form-group">
                <label>Email</label>
                <input type="email" value={email} onChange={e => setEmail(e.target.value)} placeholder="seu@email.com" required />
              </div>
              <div className="form-group">
                <label>Senha</label>
                <input type="password" value={senha} onChange={e => setSenha(e.target.value)} placeholder="Mínimo 6 caracteres" minLength={6} required />
              </div>
              <button className="btn-auth-submit" type="submit" disabled={loading}>
                {loading ? 'Aguarde...' : tab === 'entrar' ? 'Entrar' : 'Cadastrar'}
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
