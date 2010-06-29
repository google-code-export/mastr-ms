runListStore = new Ext.data.GroupingStore({
    groupField: "state",
    proxy: runStore.proxy,
    reader: runStore.reader,
    restful: true,
    remoteSort: true,
    sortInfo: {
        field: "id",
        direction: "DESC"
    }
});


MA.RunListCmp = {
    title: "runs",
    region: "center",
    cmargins: "0 0 0 0",
    collapsible: false,
    id: "runs-list",
    bodyStyle: "padding: 0",
    layout: "fit",
    tbar: [],
    items: [
        new Ext.grid.GridPanel({
            border: false,
            id: "runs",
            selModel: new Ext.grid.RowSelectionModel({ singleSelect: true }),
            view: new Ext.grid.GroupingView({
                forceFit: true,
                autoFill: true
            }),
            columns: [
                { header: "id", sortable: false, menuDisabled: true, dataIndex: "id" },
                { header: "title", sortable: false, menuDisabled: true, dataIndex: "title" },
                { header: "method", sortable: false, menuDisabled: true, dataIndex: "method__unicode" },
                { header: "machine", sortable: false, menuDisabled: true, dataIndex: "machine__unicode" },
                { header: "creator", sortable: false, menuDisabled: true, dataIndex: "creator__unicode" },
                { header: "created_on", sortable: false, menuDisabled: true, dataIndex: "created_on" },
                { header: "progress", sortable: false, menuDisabled: true, groupable: true, dataIndex: "progress" },
                { header: "state", sortable: false, menuDisabled: true, groupable: true, dataIndex: "state" }
            ],
            store: runListStore
        })
    ]
};
