const API = '/api';

async function request(path, opts = {}) {
  const token = localStorage.getItem('token');
  const headers = { 'Content-Type': 'application/json', ...(token ? { Authorization: `Bearer ${token}` } : {}), ...opts.headers };
  const res = await fetch(API + path, { ...opts, headers });
  const data = await res.json();
  if (!res.ok) throw new Error(data.erro || 'Erro na requisição');
  return data;
}

export const api = {
  cardapio: () => request('/cardapio'),
  lojaStatus: () => request('/loja/status'),
  criarPedido: (body) => request('/pedido/criar', { method: 'POST', body: JSON.stringify(body) }),
  auth: {
    register: (email, senha, nome) => request('/auth/register', { method: 'POST', body: JSON.stringify({ email, senha, nome }) }),
    login: (email, senha) => request('/auth/login', { method: 'POST', body: JSON.stringify({ email, senha }) }),
    me: () => request('/auth/me'),
    update: (data) => request('/auth/me', { method: 'PUT', body: JSON.stringify(data) }),
  },
  enderecos: {
    listar: () => request('/auth/enderecos'),
    adicionar: (dados) => request('/auth/enderecos', { method: 'POST', body: JSON.stringify(dados) }),
    remover: (id) => request(`/auth/enderecos/${id}`, { method: 'DELETE' }),
  },
  favoritos: {
    listar: () => request('/auth/favoritos'),
    adicionar: (dados) => request('/auth/favoritos', { method: 'POST', body: JSON.stringify(dados) }),
    remover: (id) => request(`/auth/favoritos/${id}`, { method: 'DELETE' }),
  },
};
