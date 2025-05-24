document.addEventListener('DOMContentLoaded', function() {
    const usersTable = document.getElementById('usersTable');
    const pagination = document.getElementById('pagination');
    const loadBtn = document.getElementById('loadUsers');
    const userCountInput = document.getElementById('userCount');
    const loadingIndicator = document.getElementById('loading');

    let currentPage = 1;
    const perPage = 100; // количество людей на странице 
    let allUsers = [];

    // Загрузка данных при старте
    loadInitialData();

    // Обработчик кнопки загрузки
    loadBtn.addEventListener('click', async function() {
        const count = parseInt(userCountInput.value);
        if (count > 0) {
            await loadNewUsers(count);
        }
    });

    async function loadInitialData() {
        // Показываем состояние загрузки
        showLoading(true);
        
        try {
            
            const apiUrl = `/users_in_db?page=${currentPage}&limit=${perPage}&nocache=${Date.now()}`;
            console.log('Fetching data from:', apiUrl);
    
           
            const response = await fetch(apiUrl, {
                headers: {
                    'Accept': 'application/json',
                    'Cache-Control': 'no-cache'
                }
            });

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(
                    errorData.message || 
                    `Server returned ${response.status} ${response.statusText}`
                );
            }

            const result = await response.json();
            console.log('API Response:', result);
    
        
            if (!result.data || !Array.isArray(result.data)) {
                throw new Error('Invalid data format: expected array in "data" field');
            }
    
            if (!result.meta || typeof result.meta !== 'object') {
                throw new Error('Invalid pagination metadata');
            }
    
           
            allUsers = result.data.map(user => ({
                id: user.id,
                externalId: user.external_id,
                fullName: `${user.first_name} ${user.last_name}`,
                firstName: user.first_name,
                lastName: user.last_name,
                email: user.email,
                phone: user.phone,
                location: `${user.city}, ${user.country}`,
                city: user.city,
                country: user.country,
                picture: user.picture_thumbnail,
                profileUrl: user.profile_url,
                gender: user.gender,
                address: `${user.street}, ${user.city}, ${user.state}, ${user.postcode}`
            }));
    
          
            currentPage = result.meta.page;
            totalPages = result.meta.total_pages;
            totalUsers = result.meta.total;
    
            console.log(`Loaded ${allUsers.length} users. Page ${currentPage} of ${totalPages}`);
            console.log(allUsers[0].profileUrl)
            
   
            updatePaginationControls();
            renderUserTable();
            
            
            updateStats();
    
        } catch (error) {
            console.error('Failed to load user data:', error);
            
            
            showErrorMessage(`Ошибка загрузки: ${error.message}`);
            
            if (process.env.NODE_ENV === 'development') {
                document.getElementById('error-details').textContent = error.stack;
            }
        } finally {
            showLoading(false);
        }
    }
    

    async function loadNewUsers(count) {
        showLoading(true);
        try {
            const response = await fetch(`/load_user?count=${count}`);
            if (!response.ok) throw new Error('Ошибка загрузки');
            
            const result = await response.json();
            if (result.success) {
                currentPage = 1;
                await loadInitialData();
                alert(`Успешно добавлено ${count} пользователей!`);
            }
        } catch (error) {
            console.error('Ошибка:', error);
            alert('Не удалось загрузить новых пользователей');
        } finally {
            showLoading(false);
        }
    }

    function renderUserTable() {
        const tableBody = document.getElementById('usersTable');
        if (!tableBody) return;

        tableBody.innerHTML = allUsers.map(user => `
            <tr data-user-id="${user.id}">
                <td class="user-avatar-cell">
                    <img src="${user.picture}" alt="${user.fullName}" class="user-avatar" 
                        onerror="this.src='/static/images/default-avatar.png'">
                </td>
                <td>${user.firstName}</td>
                <td>${user.lastName}</td>
                <td>${user.gender}</td>
                <td><a href="mailto:${user.email}">${user.email}</a></td>
                <td><a href="tel:${user.phone}">${user.phone}</a></td>
                <td>${user.location}</td>
                <td>
                    <a href="${user.profileUrl || '#'}" 
                    target="_blank" 
                    class="profile-link"
                    onclick="return validateLink(this)">
                        <i class="fas fa-external-link-alt"></i>
                    </a>
                </td>
            </tr>
        `).join('');

        //  Обработчик событий
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', () => editUser(btn.dataset.userId));
        });
    }

    function validateLink(link) {
        if (!link.href || link.href === '#' || !link.href.startsWith('http')) {
            alert('Ссылка на профиль недоступна');
            return false;
        }
        return true;
    }

    function updatePaginationControls() {
        const pagination = document.getElementById('pagination');
        if (!pagination) return;

        pagination.innerHTML = `
            <div class="pagination-container">
                <div class="pagination-info">
                    Показано ${allUsers.length} из ${totalUsers} пользователей
                </div>
                <div class="pagination-controls">
                    <button id="btn-first" ${currentPage <= 1 ? 'disabled' : ''}>
                        <i class="fas fa-angle-double-left"></i>
                        <span>В начало</span>
                    </button>
                    <button id="btn-prev" ${currentPage <= 1 ? 'disabled' : ''}>
                        <i class="fas fa-angle-left"></i>
                        <span>Назад</span>
                    </button>
                    <span class="page-info">Страница ${currentPage} из ${totalPages}</span>
                    <button id="btn-next" ${currentPage >= totalPages ? 'disabled' : ''}>
                        <i class="fas fa-angle-right"></i>
                        <span>Вперед</span>
                    </button>
                    <button id="btn-last" ${currentPage >= totalPages ? 'disabled' : ''}>
                        <i class="fas fa-angle-double-right"></i>
                        <span>В конец</span>
                    </button>
                </div>
            </div>
        `;

        // Обработчики событий
        document.getElementById('btn-first').addEventListener('click', () => {
            currentPage = 1;
            loadInitialData();
        });
        
        document.getElementById('btn-prev').addEventListener('click', () => {
            if (currentPage > 1) {
                currentPage--;
                loadInitialData();
            }
        });
        
        document.getElementById('btn-next').addEventListener('click', () => {
            if (currentPage < totalPages) {
                currentPage++;
                loadInitialData();
            }
        });
        
        document.getElementById('btn-last').addEventListener('click', () => {
            currentPage = totalPages;
            loadInitialData();
        });
    }

    function updateStats() {
        const stats = {
            male: allUsers.filter(u => u.gender === 'male').length,
            female: allUsers.filter(u => u.gender === 'female').length,
            countries: new Set(allUsers.map(u => u.country)).size
        };
        
        document.getElementById('stats-male').textContent = stats.male;
        document.getElementById('stats-female').textContent = stats.female;
        document.getElementById('stats-countries').textContent = stats.countries;
    }

    function showLoading(show) {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.style.display = show ? 'block' : 'none';
        
        const table = document.getElementById('users-table');
        if (table) table.style.opacity = show ? 0.5 : 1;
    }

    function showErrorMessage(message) {
        const errorBox = document.getElementById('error-message');
        if (errorBox) {
            errorBox.innerHTML = `
                <div class="error-content">
                    ${message}
                    <button id="retry-btn">Повторить попытку</button>
                </div>
            `;
            errorBox.style.display = 'block';
            
            document.getElementById('retry-btn').addEventListener('click', loadInitialData);
        }
    }
})
