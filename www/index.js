const dateFormat = 'DD.MM.YYYY',
      dayWidth = 15,
      monthNames = [
        'Январь',
        'Февраль',
        'Март',
        'Апрель',
        'Май',
        'Июнь',
        'Июль',
        'Август',
        'Сентябрь',
        'Октябрь',
        'Ноябрь',
        'Декабрь',
    ]
;

function renderTripper(weekendList, eventSource, tagGroups){
    // Calendar first month
    const now = moment(),
          eventList = getEvents(now, eventSource),
          firstMonth = monthBeginning(eventList[0].start),
          lastMonth = getLastMonth(eventList),
          months = getMonths(now, firstMonth, lastMonth, weekendList)
    ;

    const app = new Vue({
        el: '#app',
        data: {
            bgOffset: (firstMonth.isoWeekday() + 2) * dayWidth,
            months: months,
            tags: tagGroups,
            selectedTags: [],
        },
        filters: {
            pluralize: function(value, one, two, three){
                const cases = [2, 0, 1, 1, 1, 2],
                     titles = [one, two, three],
                        key = (value % 100 > 4 && value % 100 < 20) ? 2 : cases[(value % 10 < 5) ? value % 10 : 5]
                ;
                return titles[key];
            }
        },
        computed: {
            eventFilter(){
                let self = this,
                    events = eventList
                ;

                let selectedTags = 0;
                this.selectedTags.forEach((b) => selectedTags |= b);

                if (!selectedTags){
                    this.tags.forEach(function(g){
                        g.tags.forEach((t) => t.active = true);
                    });
                } else {
                    this.tags.forEach(function(g){
                        // Collects possible events
                        let groupEvents = eventList;
                        self.tags.forEach(function(j){
                            let bits = selectedTags & j.bits;
                            if (bits && j.bits != g.bits) {
                                groupEvents = groupEvents.filter((e) => bits & e.tags)
                            }
                        });

                        // Marks active tags
                        let eventsMask = 0;
                        groupEvents.forEach((e) => eventsMask |= e.tags);
                        g.tags.forEach((t) => t.active = eventsMask & t.bit);

                        // Filters gant events
                        let applyBits = selectedTags & g.bits;
                        if (applyBits) {
                            events = events.filter((e) => applyBits & e.tags);
                        }
                    });
                }

                events = masonry(events);
                return events;
            }
        }
    });

    const gantWidth = months.reduce((r, m) => r + m.days.length, 0) * dayWidth;
    const gantContainer = document.querySelector('.gant__container');
    gantContainer.style.height = gantContainer.scrollHeight + 'px';
    gantContainer.style.width = gantWidth + 'px';

//    const canvas = document.createElement('canvas');
//    canvas.height = 1;
//    canvas.width = gantWidth;
//    const ctx = canvas.getContext("2d");
//
//    let z = 0;
//    for (let x = 0; x < months.length; x++){
//        const m = months[x];
//        for (let y = 0; y < m.days.length; y++){
//            ctx.fillStyle = m.days[y].is_weekend ? '#fff7f7' : 'white';
//            ctx.fillRect(z * dayWidth, 0, dayWidth, 1);
//            z++
//        }
//    }
//    gantContainer.style.backgroundImage = 'url(' + canvas.toDataURL("image/png") + ')'
}


function monthBeginning(date) {
    let beginning = date.clone();
    beginning.startOf('month');
    return beginning;
}

function getLastMonth(eventList) {
    // Founds last available month from eventList
    let lastMonth = eventList[eventList.length - 1].end;
    for (let i = 0; i < eventList.length; i++) {
        let event = eventList[i];
        if (event.end > lastMonth) {
            lastMonth = event.end;
        }
    }
    return monthBeginning(lastMonth);
}

function getEvents(firstMonth, eventSource, tagGroups) {
    let eventList = [];

    for (let i = 0; i < eventSource.length; i++){
        let source = eventSource[i];
        start = moment(source.start, dateFormat);
        end = moment(source.end, dateFormat);

        // Skips old events
        if (end < firstMonth) {
            continue;
        }

        event = Object.assign(source, {
               id: 'gant__event--' + i,
            index: i,
            start: start,
              end: end,
            level: source.level,
             days: end.diff(start, 'days') + 1,
           hoffset: (start.diff(firstMonth, 'days') + firstMonth.date() - 1) * dayWidth,
           voffset: 0,
        });

        eventList.push(event);
    }

    // Must sort events
    // Smallest left, biggest right
    return eventList.sort(function(a,b) {
        if (a.start > b.start) {
            return 1;
        } else if (a.start.isSame(b.start)) {
            // Puts longest first
            return b.end - a.end;
        }
        return -1;
    });
}

function getMonths(now, firstMonth, lastMonth, weekendList){
    let monthList = [];

    // Creates months rule
    const monthLen = lastMonth.diff(firstMonth, 'months');
    for (let i = 0; ; i++) {
        let month = moment(firstMonth),
            days = [];
        month.add(i, 'month');

        let total = month.daysInMonth();
        for (let y = 0; y < total; y++){
            let d = moment(month);
            d.date(y + 1)
            days.push({
                date: d,
                is_weekend: d.isoWeekday() >= 6 || weekendList.indexOf(d.format(dateFormat)) > -1,
                is_today: d.format(dateFormat) == now.format(dateFormat),
            });
        }

        let name = monthNames[month.month()];
        if (month.month() == 0 && month.year() > now.year()) {
            name = name + ' ' + month.year()
        }

        monthList.push({
            name: name,
            days: days,
        });

        // Fixme: validate corner cases
        // May come infinite loop
        if (month >= lastMonth) {
            break;
        }
    }

    return monthList;
}

function masonry(eventList){
    let events = [],
        seen = [];
    for (let i = 0; i < eventList.length; i++) {
        let event = Object.assign({}, eventList[i]);

        // Moves event down
        // if row place is already taken.
        let found = false;
        for (let y = 0; y < seen.length; y++) {
            let other = seen[y];
            if (other.end < event.start) {
                seen[y] = event;
                event.voffset = y;
                found = true;
                break;
            }
        }

        // If row is empty
        // sets event's end as right border
        if (!found){
            event.voffset = seen.length;
            seen.push(event);
        }
        events.push(event)
    }
    return events
}

renderTripper(weekendList, eventSource, tagGroups);
document.body.classList.add('active');
setTimeout(function(){
    let blocker = document.getElementById('blocker');
    blocker.parentNode.removeChild(blocker);
}, 300);
