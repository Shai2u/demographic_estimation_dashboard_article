window.someNamespace = Object.assign({}, window.someNamespace, {
    someSubNamespace: {
        bindPopup: function (feature, layer) {
            const project_num = feature.properties.project_nu;
            layer.bindPopup(`<iframe style="max-height:400px;max-width:400px;" id="iframe" src="https://shai2u.github.io/demographic_estimation_dashboard_article/dashboard/figures/graph_${project_num}.html"></iframe>`, { maxWidth: "auto", maxHeight: "auto" })
        }
    }
});