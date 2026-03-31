#!/usr/bin/env python3

import psutil
import time

import iterm2

# Icons are base64-encoded PNGs. The first one is 32x34 and is used for Retina
# displays. The second is 16x32 and is used for non-Retina displays.
ICON1X = "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAA4klEQVQ4jdXSsUpDQRAF0BOFRCI2NpJasDSFrdjb+AGKjT+g/oKVja2tR" \
         "cr8gWilINiksFBCbAQb0UoEFVF5MIElbJ7hdV4Ydnf2DvfO7vg3mMMFHrBcxfQsfiJ204vpMQUz2MYSFuM8wCMO8VGmVpD7ieIwWjnyVC" \
         "bXwyvquErya5P0WmAn1tVEvYNNPOMMJ0Ny7g16sZ5jHi/YwD0W8I0nnP7l5CjUb8tIow4aaKOLY7xjHV8xB6W4xGfS90qQ7/A2rrCW7Lf" \
         "QDPJ1/HuBA+zHNFbCXjjKIjcHo7iZpP9qwC8MbTANfstalwAAAABJRU5ErkJggg=="

ICON2X = "iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAABmJLR0QA/wD/AP+gvaeTAAABQ0lEQVRIie3WTysEYRwH8E8iLpTCgUKKG" \
         "xeUiysvwUtQXoG8AW+CF+HI7gGLFBHWWTlwQWIvlNbBbI3dx581M1tbvvUcZn7PPJ+Z53lmGv7ThBlCHiXkMNgoOI9yrG01Cn6ugp++69" \
         "ySInz4w3FmGfIxvc/YlNIa9+HY56mstBcZbaY+XHyBZraZ4mgR81jCaQAupQlXprcY3QT04iEAb0f11jTgAo5iKKwH0DfMYBiXGE8Dj2c" \
         "mQqrhtai+EaiVowdIlJ3AoPfoiepzOA/02U0KlwKDLiYd9DfJqX3atizBAXRgBDdV+HJWaCfOfHwG2zGG2xj8iuk0oG5MYQErOFC7eydw" \
         "Fzt/khTdF34dyrjCaKzvJB5j9UQpfIEeoT/Qf/WvcPXnbbbO66/rBStJ+iPQfHDSdElpjevNE/b+Av+nYXkHMamMFtu4zVEAAAAASUVOR" \
         "K5CYII="


def get_uptime():
    boot_time = psutil.boot_time()
    system_uptime = int(time.time()) - int(boot_time)

    days = system_uptime // (24 * 3600)
    system_uptime = system_uptime % (24 * 3600)
    hours = system_uptime // 3600
    system_uptime %= 3600
    minutes = system_uptime // 60
    system_uptime %= 60
    seconds = system_uptime
    days_text = "days" if days > 1 else "day"

    if days > 0:
        return '%d %s %02d:%02d:%02d' % (days, days_text, hours, minutes, seconds)
    else:
        return '%02d:%02d:%02d' % (hours, minutes, seconds)


def get_top_processes_by_cpu(limit=10):
    """Get top processes sorted by CPU usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by CPU usage
    processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    return processes[:limit]


def get_top_processes_by_memory(limit=10):
    """Get top processes sorted by memory usage."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            pinfo = proc.info
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    
    # Sort by memory usage
    processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    return processes[:limit]


def format_process_table(processes, sort_by='cpu', text_color='inherit'):
    """Format processes as HTML table."""
    html = f'<table style="width: 100%; border-collapse: collapse; background-color: transparent;">'
    html += '<thead><tr>'
    html += f'<th style="text-align: left; padding: 8px; border-bottom: 2px solid {text_color}; color: {text_color};">PID</th>'
    html += f'<th style="text-align: left; padding: 8px; border-bottom: 2px solid {text_color}; color: {text_color};">Name</th>'
    html += f'<th style="text-align: right; padding: 8px; border-bottom: 2px solid {text_color}; color: {text_color};">CPU %</th>'
    html += f'<th style="text-align: right; padding: 8px; border-bottom: 2px solid {text_color}; color: {text_color};">Memory %</th>'
    html += '</tr></thead>'
    html += '<tbody>'
    
    for proc in processes:
        pid = proc.get('pid', 'N/A')
        name = proc.get('name', 'N/A')
        cpu = proc.get('cpu_percent', 0) or 0
        mem = proc.get('memory_percent', 0) or 0
        
        # Truncate long process names
        if len(name) > 30:
            name = name[:27] + '...'
        
        html += '<tr>'
        html += f'<td style="padding: 6px 8px; color: {text_color};">{pid}</td>'
        html += f'<td style="padding: 6px 8px; color: {text_color};">{name}</td>'
        html += f'<td style="padding: 6px 8px; text-align: right; color: {text_color};">{cpu:.1f}%</td>'
        html += f'<td style="padding: 6px 8px; text-align: right; color: {text_color};">{mem:.1f}%</td>'
        html += '</tr>'
    
    html += '</tbody></table>'
    return html


async def main(connection):
    app = await iterm2.async_get_app(connection)
    icon1x = iterm2.StatusBarComponent.Icon(1, ICON1X)
    icon2x = iterm2.StatusBarComponent.Icon(2, ICON2X)

    component = iterm2.StatusBarComponent(
        short_description="Uptime",
        detailed_description="Shows the system uptime since boot",
        knobs=[],
        exemplar='🏃' + get_uptime(),
        update_cadence=1,
        identifier="catj.moe.uptime",
        icons=[icon1x, icon2x])

    # This function gets called once per second.
    @iterm2.StatusBarRPC
    async def uptime(knobs):
        return get_uptime()

    @iterm2.RPC
    async def onclick(session_id):
        session = app.get_session_by_id(session_id)
        # Get the session's profile to access background color
        profile = await session.async_get_profile()
        background_color = profile.background_color
        
        # Convert background color to CSS format
        bg_color_css = f"rgba({int(background_color.red)}, {int(background_color.green)}, {int(background_color.blue)}, {background_color.alpha})"
        
        # Calculate opposite text color (simple inversion)
        text_red = 255 - int(background_color.red)
        text_green = 255 - int(background_color.green)
        text_blue = 255 - int(background_color.blue)
        text_color_css = f"rgb({text_red}, {text_green}, {text_blue})"

        # Get top processes
        top_cpu = get_top_processes_by_cpu(10)
        top_memory = get_top_processes_by_memory(10)
        
        # Format tables
        cpu_table = format_process_table(top_cpu, 'cpu', text_color_css)
        memory_table = format_process_table(top_memory, 'memory', text_color_css)

        html_content = f"""
        <html style="margin: 0; padding: 0; background-color: {bg_color_css}; width: 100%; height: 100%; border-radius: 8px; overflow: hidden;">
        <head>
            <style>
                html, body {{
                    margin: 0 !important;
                    padding: 0 !important;
                    background-color: {bg_color_css} !important;
                    color: {text_color_css} !important;
                    border: none !important;
                    outline: none !important;
                    width: 100% !important;
                    height: 100% !important;
                    border-radius: 8px !important;
                    overflow: hidden !important;
                    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro', monospace;
                }}
                
                .container {{
                    padding: 10px;
                    height: 100%;
                    box-sizing: border-box;
                    display: flex;
                    flex-direction: column;
                }}
                
                .tabs {{
                    display: flex;
                    border-bottom: 2px solid {text_color_css};
                    margin-bottom: 10px;
                }}
                
                .tab {{
                    padding: 10px 20px;
                    cursor: pointer;
                    background-color: transparent;
                    color: {text_color_css};
                    border: none;
                    border-bottom: 3px solid transparent;
                    font-size: 14px;
                    font-weight: 500;
                    transition: all 0.2s;
                }}
                
                .tab:hover {{
                    opacity: 0.7;
                }}
                
                .tab.active {{
                    border-bottom-color: {text_color_css};
                    font-weight: 600;
                }}
                
                .tab-content {{
                    display: none;
                    flex: 1;
                    overflow: auto;
                }}
                
                .tab-content.active {{
                    display: block;
                }}
                
                table {{
                    width: 100% !important;
                    background-color: transparent !important;
                    color: {text_color_css} !important;
                    border-collapse: collapse;
                    font-size: 12px;
                }}
                
                th {{
                    text-align: left;
                    padding: 8px !important;
                    border-bottom: 2px solid {text_color_css};
                    color: {text_color_css} !important;
                    font-weight: 600;
                    background-color: transparent !important;
                }}
                
                td {{
                    padding: 6px 8px !important;
                    color: {text_color_css} !important;
                    background-color: transparent !important;
                    border: none !important;
                }}
                
                tr:hover {{
                    background-color: rgba({text_red}, {text_green}, {text_blue}, 0.1) !important;
                }}
                
                h2 {{
                    margin: 0 0 10px 0;
                    padding: 0;
                    color: {text_color_css} !important;
                    font-size: 16px;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Top 10 Processes</h2>
                <div class="tabs">
                    <button class="tab active" onclick="showTab('cpu')">CPU Usage</button>
                    <button class="tab" onclick="showTab('memory')">Memory Usage</button>
                </div>
                
                <div id="cpu-content" class="tab-content active">
                    {cpu_table}
                </div>
                
                <div id="memory-content" class="tab-content">
                    {memory_table}
                </div>
            </div>
            
            <script>
                function showTab(tabName) {{
                    // Hide all tab contents
                    var contents = document.getElementsByClassName('tab-content');
                    for (var i = 0; i < contents.length; i++) {{
                        contents[i].classList.remove('active');
                    }}
                    
                    // Remove active class from all tabs
                    var tabs = document.getElementsByClassName('tab');
                    for (var i = 0; i < tabs.length; i++) {{
                        tabs[i].classList.remove('active');
                    }}
                    
                    // Show selected tab content
                    document.getElementById(tabName + '-content').classList.add('active');
                    
                    // Add active class to clicked tab
                    event.target.classList.add('active');
                }}
            </script>
        </body>
        </html>
        """
        
        await component.async_open_popover(session_id, html_content, iterm2.util.Size(620, 480))

    # Register the component.
    await component.async_register(connection, uptime, onclick=onclick)


iterm2.run_forever(main)
