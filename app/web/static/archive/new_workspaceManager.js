// new_workspaceManager.js - 处理工作区文件显示

export class WorkspaceManager {
    constructor(fileClickCallback) {
        this.workspaceContainer = document.getElementById('workspace-files');
        this.fileClickCallback = fileClickCallback;
        this.workspaces = [];
        this.refreshTimer = null;
    }

    // 初始化工作区管理器
    init() {
        // 设置自动刷新计时器
        this.startRefreshTimer();
    }

    // 更新工作区列表
    updateWorkspaces(workspaces) {
        if (!Array.isArray(workspaces)) return;

        this.workspaces = workspaces;
        this.renderWorkspaces();
    }

    // 渲染工作区列表
    renderWorkspaces() {
        // 清空容器
        this.workspaceContainer.innerHTML = '';

        // 如果没有工作区，显示提示信息
        if (this.workspaces.length === 0) {
            const emptyDiv = document.createElement('div');
            emptyDiv.className = 'empty-workspace';
            emptyDiv.textContent = 'No workspace files';
            this.workspaceContainer.appendChild(emptyDiv);
            return;
        }

        // 渲染每个工作区
        this.workspaces.forEach(workspace => {
            // 创建工作区项
            const workspaceItem = this.createWorkspaceItem(workspace);
            this.workspaceContainer.appendChild(workspaceItem);

            // 渲染工作区下的文件
            if (workspace.files && workspace.files.length > 0) {
                workspace.files.forEach(file => {
                    const fileItem = this.createFileItem(file);
                    this.workspaceContainer.appendChild(fileItem);
                });
            }
        });
    }

    // 创建工作区项
    createWorkspaceItem(workspace) {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'workspace-item';

        // 创建图标
        const iconDiv = document.createElement('div');
        iconDiv.className = 'workspace-icon';
        iconDiv.textContent = '📁';
        itemDiv.appendChild(iconDiv);

        // 创建详情容器
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'workspace-details';

        // 创建工作区名称
        const nameDiv = document.createElement('div');
        nameDiv.className = 'workspace-name';
        nameDiv.textContent = workspace.name;
        detailsDiv.appendChild(nameDiv);

        // 创建修改时间
        const dateDiv = document.createElement('div');
        dateDiv.className = 'workspace-date';
        dateDiv.textContent = this.formatDate(workspace.modified);
        detailsDiv.appendChild(dateDiv);

        itemDiv.appendChild(detailsDiv);
        return itemDiv;
    }

    // 创建文件项
    createFileItem(file) {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'file-item';

        // 创建图标
        const iconDiv = document.createElement('div');
        iconDiv.className = 'file-icon';
        iconDiv.textContent = this.getFileIcon(file.type);
        itemDiv.appendChild(iconDiv);

        // 创建详情容器
        const detailsDiv = document.createElement('div');
        detailsDiv.className = 'file-details';

        // 创建文件名称
        const nameDiv = document.createElement('div');
        nameDiv.className = 'file-name';
        nameDiv.textContent = file.name;
        detailsDiv.appendChild(nameDiv);

        // 创建文件元信息
        const metaDiv = document.createElement('div');
        metaDiv.className = 'file-meta';
        metaDiv.textContent = `${this.formatFileSize(file.size)} · ${this.formatDate(file.modified)}`;
        detailsDiv.appendChild(metaDiv);

        itemDiv.appendChild(detailsDiv);

        // 绑定点击事件
        itemDiv.addEventListener('click', () => {
            if (this.fileClickCallback) {
                this.fileClickCallback(file.path);
            }
        });

        return itemDiv;
    }

    // 获取文件图标
    getFileIcon(fileType) {
        switch (fileType) {
            case 'txt':
                return '📄';
            case 'md':
                return '📝';
            case 'html':
                return '🌐';
            case 'css':
                return '🎨';
            case 'js':
                return '📜';
            case 'py':
                return '🐍';
            case 'json':
                return '📊';
            default:
                return '📄';
        }
    }

    // 格式化文件大小
    formatFileSize(size) {
        if (size < 1024) {
            return `${size} B`;
        } else if (size < 1024 * 1024) {
            return `${(size / 1024).toFixed(0)} KB`;
        } else {
            return `${(size / (1024 * 1024)).toFixed(1)} MB`;
        }
    }

    // 格式化日期
    formatDate(timestamp) {
        if (!timestamp) return '';

        const date = new Date(timestamp * 1000);
        return date.toLocaleString();
    }

    // 开始自动刷新计时器
    startRefreshTimer() {
        // 清除现有计时器
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
        }

        // 设置新计时器，每5秒刷新一次
        this.refreshTimer = setInterval(() => {
            // 更新倒计时显示
            const refreshSpan = document.querySelector('.refresh-info span');
            if (refreshSpan) {
                const seconds = parseInt(refreshSpan.textContent.match(/\d+/)[0] || 5);
                if (seconds > 1) {
                    refreshSpan.textContent = `Refresh after ${seconds - 1} seconds`;
                } else {
                    refreshSpan.textContent = 'Refreshing...';
                    // 触发刷新
                    this.refreshWorkspaces();
                }
            }
        }, 1000);
    }

    // 刷新工作区文件
    async refreshWorkspaces() {
        try {
            const response = await fetch('/api/files');
            if (!response.ok) {
                throw new Error(`API错误: ${response.status}`);
            }

            const data = await response.json();
            this.updateWorkspaces(data.workspaces);

            // 重置倒计时
            const refreshSpan = document.querySelector('.refresh-info span');
            if (refreshSpan) {
                refreshSpan.textContent = 'Refresh after 5 seconds';
            }

        } catch (error) {
            console.error('刷新工作区文件错误:', error);
        }
    }
}
