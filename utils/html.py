"""

Utils to create html files with a combination of Plotly plots

"""
import plotly.io as pio


def combine_plots(figures, row_width=1300):

    html = f"<div style='width: {row_width}px;'>"

    for row in figures:
        html += "<div style='display: flex;'>"
        width = int(row_width / len(row))
        for fig in row:
            html += f"<div style='flex: 1;'><div style='width: {width}px;'>"
            if fig is not None:
                html += pio.to_html(
                    fig.update_layout(width=width),
                    include_plotlyjs=False,
                    full_html=False,
                )
            html += "</div></div>"
        html += "</div>"

    html += "</div>"

    return html


def full_html(tab_names, tab_contents, outputname):
    html = """
    <html><head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js"></script></head><body style="padding: 10px;"><script type="text/javascript">window.PlotlyConfig = {MathJaxConfig: 'local'};</script>        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    """

    # Create the tab buttons
    html += """
    """
    html += tab_buttons(tab_names)

    # Combine the tab contents
    html += '<div class="tab-content">'
    for i, content in enumerate(tab_contents):
        active = " in active" if i == 0 else ""
        html += f'<div id="tab{i}" class="tab-pane{active}">'
        html += content
        html += "</div>"
    html += "</div>"

    # Close html
    html += "</body></html>"

    with open(outputname, "w") as file:
        file.write(html)


def tab_buttons(names):
    html = '<ul class="nav nav-pills sticky-top mb-3" style="background: rgba(255,255,255,.9);" id="pills-tab" role="tablist">'
    for i, name in enumerate(names):
        active = " active" if i == 0 else ""
        selected = "true" if i == 0 else "false"
        html += f"""
        <li class="nav-item{active}">
            <a class="nav-link{active}" id="pill-tab{i}" data-toggle="pill" href="#tab{i}" role="tab" aria-controls="#tab{i}" aria-selected="{selected}">{name}</a>
        </li>
        """
    html += "</ul>"
    return html
